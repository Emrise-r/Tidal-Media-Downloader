import os
import re
from setuptools import setup, find_packages

_here = os.path.abspath(os.path.dirname(__file__))

# Read VERSION from tidal_dl/printf.py without importing the package (the package
# uses flat imports that only resolve at runtime, not during the build).
with open(os.path.join(_here, 'tidal_dl', 'printf.py'), encoding='utf-8') as _f:
    VERSION = re.search(r"^VERSION\s*=\s*['\"]([^'\"]+)['\"]", _f.read(), re.M).group(1)

# Use the repo README as the PyPI long description when available.
_long_description = "Tidal Music Downloader with OAuth2 PKCE login and HI_RES_LOSSLESS support."
try:
    with open(os.path.join(_here, '..', 'README.md'), encoding='utf-8') as _f:
        _long_description = _f.read()
except OSError:
    pass

setup(
    name='tidal-dl-max',
    version=VERSION,
    license="Apache-2.0",
    description="Tidal Music Downloader with OAuth2 PKCE login and HI_RES_LOSSLESS "
                "support (fork of yaronzz/Tidal-Media-Downloader).",
    long_description=_long_description,
    long_description_content_type="text/markdown",

    author='emrise',
    author_email="nqvinh98@gmail.com",
    url="https://github.com/Emrise-r/Tidal-Media-Downloader",

    packages=find_packages(exclude=['tidal_gui*']),
    include_package_data=False,
    platforms="any",
    python_requires=">=3.10",
    install_requires=["aigpy>=2022.7.8.1",
                      "requests>=2.22.0",
                      "pycryptodome",
                      "pydub",
                      "prettytable"],
    entry_points={'console_scripts': ['tidal-dl = tidal_dl:main', ]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
