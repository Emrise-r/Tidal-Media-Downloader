#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  pkce_windows.py
@Desc    :  Windows tidal:// scheme registration strategy.

            Registers a per-user URL-protocol handler under
            HKCU\\Software\\Classes\\tidal so the browser redirect from the PKCE
            login is delivered to `tidal-dl --auth-callback <url>`.
"""
from pkce import SchemeStrategy


class WindowsSchemeStrategy(SchemeStrategy):
    # Shown by the browser's "Open ___?" prompt — make it clearly this CLI,
    # not the TIDAL desktop app, so users know it's the login helper.
    DISPLAY_NAME = 'URL:tidal-dl login helper'

    def register(self):
        import winreg

        command = self.launch_command('"%1"', quote=lambda s: '"%s"' % s)
        base = r'Software\Classes\%s' % self.scheme
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base) as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, self.DISPLAY_NAME)
            winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, '')
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base + r'\shell\open\command') as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, command)
        return True
