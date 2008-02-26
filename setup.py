#!/usr/bin/env python

import os
import re

from setuptools import setup, find_packages

import pymills

# borrowed from pymills.utils
def getFiles(paths, tests=[os.path.isfile], pattern=".*", \
		include_path=True):
	"""getFiles(path, tests=[os.path.isfile], pattern=".*", \
			include_path=True) -> list of files

	Return a list of files in the specified path
	applying the predicates listed in tests returning
	only the files that match the pattern.
	"""

	def testFile(file):
		for test in tests:
			if not test(file):
				return False
		return True

	list = []
	for path in paths:
		if not os.path.exists(path):
			continue
		files = os.listdir(path)
		for file in files:
			if testFile(os.path.join(path, file)) and \
					re.match(pattern, file):
				if include_path:
					list.append(os.path.join(path, file))
				else:
					list.append(file)
	return list

setup(
		name='pymills',
		version=pymills.__version__,
		description=pymills.__description__,
		long_description=pymills.__doc__,
		author=pymills.__author__,
		author_email=pymills.__author_email__,
		maintainer=pymills.__maintainer__,
		maintainer_email=pymills.__maintainer_email__,
		url=pymills.__url__,
		download_url=pymills.__download_url__,
		classifiers=pymills.__classifiers__,
		license=pymills.__license__,
		keywords=pymills.__keywords__,
		platforms=pymills.__platforms__,
		packages=find_packages(),
		scripts=getFiles(["scripts"]),
		install_requires=pymills.__install_requires__,
		setup_requires=pymills.__setup_requires__,
		extras_require=pymills.__extras_require__,
		entry_points=pymills.__entry_points__,
		package_data=pymills.__package_data__,
)
