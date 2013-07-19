#!/usr/bin/env python

from setuptools import setup, find_packages

from pymills.version import forget_version, get_version, remember_version

forget_version()
version = remember_version()

setup(
    name="pymills",
    version=get_version(),
    description="Mills Python Library",
    long_description=open("README.rst", "r").read(),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="http://bitbucket.org/prologic/pymills/",
    download_url="http://bitbucket.org/prologic/pymills/downloads/",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.6",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MIT",
    keywords="James Mills Python Library Utilities Modules",
    platforms="POSIX",
    packages=find_packages("."),
)
