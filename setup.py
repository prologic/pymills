#!/usr/bin/env python

from distutils.core import setup

import pymills

setup(name = "pymills",
		version = pymills.__version__,
		description = pymills.__desc__,
		author = pymills.__author__,
		author_email = pymills.__email__,
		url = pymills.__url__,
		packages=["pymills"])
