#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  pkce_linux.py
@Desc    :  Linux tidal:// scheme registration strategy.

            Writes a NoDisplay .desktop entry that handles
            x-scheme-handler/tidal and makes it the default via xdg-mime, so the
            browser redirect is delivered to `tidal-dl --auth-callback <url>`.
"""
import os
import shlex
import shutil
import subprocess

from pkce import SchemeStrategy


class LinuxSchemeStrategy(SchemeStrategy):
    def register(self):
        apps_dir = os.path.join(self.home_path(), '.local', 'share', 'applications')
        os.makedirs(apps_dir, exist_ok=True)
        desktop = os.path.join(apps_dir, 'tidal-dl.desktop')

        exec_line = self.launch_command('%u', quote=shlex.quote)
        content = (
            "[Desktop Entry]\n"
            "Name=tidal-dl\n"
            "Comment=TIDAL login callback handler\n"
            "Exec=%s\n"
            "Type=Application\n"
            "Terminal=false\n"
            "NoDisplay=true\n"
            "MimeType=x-scheme-handler/%s;\n" % (exec_line, self.scheme)
        )
        with open(desktop, 'w') as f:
            f.write(content)

        if shutil.which('xdg-mime'):
            subprocess.run(['xdg-mime', 'default', 'tidal-dl.desktop',
                            'x-scheme-handler/%s' % self.scheme], check=False)
        if shutil.which('update-desktop-database'):
            subprocess.run(['update-desktop-database', apps_dir], check=False)
        return True
