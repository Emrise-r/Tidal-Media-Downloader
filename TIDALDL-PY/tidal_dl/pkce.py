#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  pkce.py
@Desc    :  OAuth2 authorization-code + PKCE helpers for the "gcloud-style" login:
            open the browser (with fallbacks), receive the authorization code via a
            localhost loopback server, and register the `tidal://` URL scheme so the
            browser redirect is delivered back to the running CLI.

            The Tidal PKCE client's redirect is a custom scheme (tidal://login/auth).
            After the user authorizes, the browser navigates to that scheme; the OS
            hands it to the registered handler `tidal-dl --auth-callback <url>`, which
            forwards the code to the still-running login session's loopback server.
            Manual paste of the redirected URL/code is the final fallback.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import requests

SCHEME = "tidal"
DEFAULT_PORT = 8989


# ----------------------------------------------------------------------------
# Paths (kept local so this module has no heavy imports / import cycles)
# ----------------------------------------------------------------------------
def _home_path():
    if "XDG_CONFIG_HOME" in os.environ:
        return os.environ['XDG_CONFIG_HOME']
    elif "HOME" in os.environ:
        return os.environ['HOME']
    elif "HOMEDRIVE" in os.environ and "HOMEPATH" in os.environ:
        return os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    return os.path.abspath("./")


def _callback_info_path():
    return os.path.join(_home_path(), '.tidal-dl.authcb.json')


def _scheme_marker_path():
    return os.path.join(_home_path(), '.tidal-dl.scheme')


def _authcode_path():
    # Shared file the scheme handler writes the code to, so the waiting login
    # process can pick it up even when the loopback port can't bind.
    return os.path.join(_home_path(), '.tidal-dl.authcode')


def clear_authcode():
    try:
        os.remove(_authcode_path())
    except Exception:
        pass


def _write_authcode(code, state):
    try:
        with open(_authcode_path(), 'w') as f:
            json.dump({'code': code, 'state': state}, f)
        return True
    except Exception:
        return False


def _read_authcode(expected_state):
    try:
        with open(_authcode_path()) as f:
            data = json.load(f)
    except Exception:
        return None
    code = data.get('code')
    state = data.get('state')
    if code and (expected_state is None or state == expected_state):
        return code
    return None


def _write_callback_info(port, state):
    try:
        with open(_callback_info_path(), 'w') as f:
            json.dump({'port': port, 'state': state}, f)
    except Exception:
        pass


def _read_callback_info():
    try:
        with open(_callback_info_path()) as f:
            return json.load(f)
    except Exception:
        return None


def _clear_callback_info():
    try:
        os.remove(_callback_info_path())
    except Exception:
        pass


# ----------------------------------------------------------------------------
# Code parsing
# ----------------------------------------------------------------------------
def parse_code(text):
    """Extract (code, state) from a redirect URL, a query string, or a bare code."""
    if not text:
        return None, None
    text = text.strip().strip('"').strip("'")
    if 'code=' in text:
        query = urlparse(text).query or text
        qs = parse_qs(query)
        code = (qs.get('code') or [None])[0]
        state = (qs.get('state') or [None])[0]
        return code, state
    # assume a bare authorization code
    return text or None, None


# ----------------------------------------------------------------------------
# Browser
# ----------------------------------------------------------------------------
def _is_termux():
    return 'com.termux' in os.environ.get('PREFIX', '') or bool(os.environ.get('ANDROID_ROOT')) \
        or shutil.which('termux-open-url') is not None


def open_browser(url):
    """Best-effort open the URL in a browser. Returns True if a browser was launched."""
    # Android / Termux: the stdlib webbrowser usually can't help.
    if _is_termux():
        opener = shutil.which('termux-open-url')
        if opener:
            try:
                subprocess.Popen([opener, url])
                return True
            except Exception:
                return False
        return False
    try:
        return webbrowser.open(url, new=2)
    except Exception:
        return False


# ----------------------------------------------------------------------------
# Loopback callback server
# ----------------------------------------------------------------------------
class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        code = (qs.get('code') or [None])[0]
        state = (qs.get('state') or [None])[0]

        expected = getattr(self.server, 'expected_state', None)
        ok = bool(code) and (expected is None or state == expected)
        if ok:
            self.server.auth_code = code
            self.server.auth_event.set()
            body = b"<html><body><h2>TIDAL login complete.</h2>You may close this tab.</body></html>"
            self.send_response(200)
        else:
            body = b"<html><body><h3>Login callback missing or invalid.</h3></body></html>"
            self.send_response(400)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def log_message(self, *args):
        pass  # keep the console quiet


class CallbackServer:
    def __init__(self, port=DEFAULT_PORT, state=None):
        self.port = port or DEFAULT_PORT
        self.state = state
        self.event = threading.Event()
        self._httpd = None
        self._thread = None

    def start(self):
        """Bind and start serving in a daemon thread. Returns True on success."""
        try:
            self._httpd = HTTPServer(('127.0.0.1', self.port), _Handler)
        except Exception:
            self._httpd = None
            return False
        self._httpd.auth_event = self.event
        self._httpd.auth_code = None
        self._httpd.expected_state = self.state
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        _write_callback_info(self.port, self.state)
        return True

    @property
    def auth_code(self):
        return getattr(self._httpd, 'auth_code', None) if self._httpd else None

    def stop(self):
        try:
            if self._httpd:
                self._httpd.shutdown()
                self._httpd.server_close()
        except Exception:
            pass
        _clear_callback_info()


def wait_for_code(server, timeout=300, allow_paste=True, expected_state=None):
    """
    Wait up to `timeout` seconds for an authorization code from any of three
    sources: the loopback server (scheme handler forwarded it over localhost),
    the shared code file (scheme handler wrote it there), or the user pasting the
    redirected URL/code at the prompt. Returns the code or None.
    """
    result = {'code': None}

    if allow_paste:
        def _reader():
            try:
                line = input()
            except (EOFError, KeyboardInterrupt):
                return
            code, _ = parse_code(line)
            if code:
                result['code'] = code

        threading.Thread(target=_reader, daemon=True).start()

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if server is not None and server.event.is_set():
            return server.auth_code
        if result['code']:
            return result['code']
        code = _read_authcode(expected_state)
        if code:
            return code
        time.sleep(0.3)
    return None


# ----------------------------------------------------------------------------
# Scheme-handler delivery (invoked as `tidal-dl --auth-callback <url>`)
# ----------------------------------------------------------------------------
def deliver_callback(url):
    """Forward a captured redirect URL/code to the waiting login session's server."""
    code, state = parse_code(url)
    if not code:
        return False
    # 1) Shared file: works even if the loopback port never bound.
    _write_authcode(code, state)
    # 2) Loopback server: fast path when the port is up.
    info = _read_callback_info()
    port = (info.get('port') if info else None) or DEFAULT_PORT
    params = {'code': code}
    if state:
        params['state'] = state
    try:
        requests.get('http://127.0.0.1:%d/callback' % port, params=params, timeout=10)
    except Exception:
        pass
    return True


# ----------------------------------------------------------------------------
# OS URL-scheme registration (Strategy pattern)
#
# The concrete per-OS strategies live in their own modules — pkce_windows /
# pkce_linux / pkce_macos — and are imported lazily so importing this module
# never pulls in platform-specific machinery (e.g. winreg). The base class and
# the shared plumbing (launch command, home dir, cli lookup) stay here.
# ----------------------------------------------------------------------------
def _cli_executable():
    """Path to the installed console script, or None if it isn't on PATH."""
    return shutil.which('tidal-dl')


class SchemeStrategy:
    """
    Base strategy for registering the `tidal://` URL scheme to point at this CLI.

    A subclass implements register() for a single OS. Everything platform-neutral
    (building the handler command, resolving the home dir and scheme name) is
    provided here, so each OS module holds only its own registration code.
    """

    def __init__(self, scheme, home_path, cli_executable):
        self.scheme = scheme
        self._home_path = home_path
        self._cli_executable = cli_executable

    def home_path(self):
        return self._home_path()

    def launch_command(self, arg, quote):
        """
        Build the '<cli> --auth-callback <arg>' handler command, falling back to
        'python -m tidal_dl ...' when the console script isn't on PATH. `arg` is
        the OS redirect-URL placeholder ("%1", %u, "$1"); `quote` wraps the
        executable path for that platform's shell/registry syntax.
        """
        exe = self._cli_executable()
        if exe:
            return quote(exe) + ' --auth-callback ' + arg
        return quote(sys.executable) + ' -m tidal_dl --auth-callback ' + arg

    def register(self):
        """Register the scheme with the OS. Return True on success."""
        raise NotImplementedError


def _make_scheme_strategy():
    """Return a SchemeStrategy for the current OS, or None if unsupported."""
    if _is_termux():
        return None  # Android/Termux: no OS scheme registration; manual paste is used
    system = platform.system()
    if system == 'Windows':
        from pkce_windows import WindowsSchemeStrategy as Strategy
    elif system == 'Darwin':
        from pkce_macos import MacosSchemeStrategy as Strategy
    elif system == 'Linux':
        from pkce_linux import LinuxSchemeStrategy as Strategy
    else:
        return None
    return Strategy(SCHEME, _home_path, _cli_executable)


def register_scheme(force=False):
    """
    Register the `tidal://` URL scheme to point at this CLI, once per machine.
    Idempotent via a marker file. Never raises — returns bool.
    """
    marker = _scheme_marker_path()
    if not force and os.path.exists(marker):
        return True

    try:
        strategy = _make_scheme_strategy()
        ok = strategy.register() if strategy else False
    except Exception:
        ok = False

    # Write the marker regardless so we don't retry noisily every launch.
    try:
        with open(marker, 'w') as f:
            f.write('%s\n' % platform.system())
    except Exception:
        pass
    return ok
