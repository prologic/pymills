#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    HAS_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    HAS_SETUPTOOLS = False

if not HAS_SETUPTOOLS:
    import os
    from distutils.util import convert_path

    def find_packages(where=".", exclude=()):
        """Borrowed directly from setuptools"""

        out = []
        stack = [(convert_path(where), "")]
        while stack:
            where, prefix = stack.pop(0)
            for name in os.listdir(where):
                fn = os.path.join(where, name)
                if ("." not in name and os.path.isdir(fn) and 
                        os.path.isfile(os.path.join(fn, "__init__.py"))):
                    out.append(prefix+name)
                    stack.append((fn, prefix + name + "."))

        from fnmatch import fnmatchcase
        for pat in list(exclude) + ["ez_setup"]:
            out = [item for item in out if not fnmatchcase(item, pat)]

        return out

from pymills.version import forget_version, get_version, remember_version

forget_version()
version = remember_version()

setup(
    name="pymills",
    version=get_version(),
    description="Mills Python Library",
    long_description=open("README", "r").read(),
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
