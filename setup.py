#!/usr/bin/env python

from distutils.core import setup

import pymills

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

__version__ = pymills.__version__

setup(name="pymills",
		version=pymills.__version__,
		description=pymills.__desc__,
		author=pymills.__author__,
		author_email=pymills.__email__,
		url=pymills.__url__,
		license=pymills.__license__,
		keywords="James Mills general purpose python library",
		packages=[
			"pymills"],
		install_requires=["pysqlite"])
