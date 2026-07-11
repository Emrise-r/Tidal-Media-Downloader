import re
from setuptools import setup, find_packages

# Read VERSION from tidal_dl/printf.py without importing the package (the package
# uses flat imports that only resolve at runtime, not during the build).
with open('tidal_dl/printf.py', encoding='utf-8') as _f:
    VERSION = re.search(r"^VERSION\s*=\s*['\"]([^'\"]+)['\"]", _f.read(), re.M).group(1)

setup(
    name='tidal-dl',
    version=VERSION,
    license="Apache2",
    description="Tidal Music Downloader.",

    author='YaronH',
    author_email="yaronhuang@foxmail.com",

    packages=find_packages(exclude=['tidal_gui*']),
    include_package_data=False,
    platforms="any",
    install_requires=["aigpy>=2022.7.8.1", 
                      "requests>=2.22.0",
                      "pycryptodome", 
                      "pydub", 
                      "prettytable",
                      "lxml"],
    entry_points={'console_scripts': ['tidal-dl = tidal_dl:main', ]}
)
