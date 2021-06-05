# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

setup(
    name = 'ncmplex',
    version = '1.2.0',
    description = 'command line tool to export netease cloudmusic playlists to standard .m3u8',
    url = 'https://github.com/mkmark/netease-cloudmusic-playlist-exporter',
    author = 'mkmark',
    author_email = 'mark@mkmark.net',
    license = 'GNU',
    packages = find_packages(),
    platforms = 'any',
    zip_safe = False,
    python_requires = '>=3.4',
    entry_points = {
        'console_scripts': [
            'ncmplex=ncmplex.app:main'
        ]
    }
)