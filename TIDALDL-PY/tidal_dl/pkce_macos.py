#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  pkce_macos.py
@Desc    :  macOS tidal:// scheme registration strategy.

            Builds a minimal .app bundle that declares the tidal URL scheme and
            registers it with LaunchServices, so the browser redirect is
            delivered to `tidal-dl --auth-callback <url>`.
"""
import os
import shlex
import subprocess

from pkce import SchemeStrategy

_INFO_PLIST = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
    '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
    '<plist version="1.0"><dict>\n'
    '  <key>CFBundleIdentifier</key><string>com.tidal-dl.scheme</string>\n'
    '  <key>CFBundleName</key><string>tidal-dl-scheme</string>\n'
    '  <key>CFBundleExecutable</key><string>run</string>\n'
    '  <key>CFBundleURLTypes</key><array><dict>\n'
    '    <key>CFBundleURLName</key><string>com.tidal-dl.scheme</string>\n'
    '    <key>CFBundleURLSchemes</key><array><string>%s</string></array>\n'
    '  </dict></array>\n'
    '</dict></plist>\n'
)

_LSREGISTER = ('/System/Library/Frameworks/CoreServices.framework/Frameworks/'
               'LaunchServices.framework/Support/lsregister')


class MacosSchemeStrategy(SchemeStrategy):
    def register(self):
        launch = self.launch_command('"$1"', quote=shlex.quote)
        app = os.path.join(self.home_path(), 'Applications', 'tidal-dl-scheme.app')
        macos_dir = os.path.join(app, 'Contents', 'MacOS')
        os.makedirs(macos_dir, exist_ok=True)

        info_plist = os.path.join(app, 'Contents', 'Info.plist')
        with open(info_plist, 'w') as f:
            f.write(_INFO_PLIST % self.scheme)

        run = os.path.join(macos_dir, 'run')
        with open(run, 'w') as f:
            f.write('#!/bin/sh\n%s\n' % launch)
        os.chmod(run, 0o755)

        if os.path.exists(_LSREGISTER):
            subprocess.run([_LSREGISTER, '-R', '-f', app], check=False)
        return True
