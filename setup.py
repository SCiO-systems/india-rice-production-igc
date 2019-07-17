'''Setup script

Usage: pip install .

To install development dependencies too, run pip install .[dev]
'''

from setuptools import find_packages
from setuptools import setup

from _version import __version__

setup(
    name='project',
    version=__version__,
    packages=find_packages(),
    scripts=[],
    author='Georgios Chochlakis',
    url='https://github.com/SCiO-systems/Internship-George-Chochlakis',
    install_requires=[],
    extras_require={
        'dev': [
            'GDAL==2.4.0',
            'numpy',
            'matplotlib',
            'pylint',
            'git-pylint-commit-hook',
        ]
    }
)
