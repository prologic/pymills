#!/usr/bin/env python

from glob import glob
from os import getcwd, path
from imp import new_module

from setuptools import setup, find_packages


version = new_module("version")

exec(
    compile(open(path.join(path.dirname(globals().get("__file__", path.join(getcwd(), "pymills"))), "pymills/version.py"), "r").read(), "pymills/version.py", "exec"),
    version.__dict__
)


setup(
    name="pymills",
    version=version.version,
    description="Mills Python Library",
    long_description="{0:s}\n\n{1:s}".format(
        open("README.rst").read(), open("CHANGES.rst").read()
    ),
    author="James Mills",
    author_email="James Mills, j dot mills at griffith dot edu dot au",
    url="https://bitbucket.org/prologic/pymills",
    download_url="https://bitbucket.org/prologic/pymills/downloads/",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MIT",
    keywords="James Mills Python Library Utilities Modules",
    platforms="POSIX",
    packages=find_packages("."),
    scripts=glob("bin/*"),
    dependency_links=[
    ],
    install_requires=[
    ],
    entry_points={
        "console_scripts": [
        ]
    },
    test_suite="tests.main.main",
    zip_safe=True
)
