# Filename: ver.py
# Module:	ver
# Date:		07th June 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Version Library

This module contains a class to deal with version strings
and is capable of comparing versions in various formats
"""

import re
import string

class Error(Exception):
	pass

FORMATS = [
	"((?:[0-9]+\.?)+)(?:([a-zA-Z]+)([0-9]+)?)?(?:-([0-9]+))?$",
	"((?:[0-9]+_?)+)$"]

class Version:

	def __init__(self, verStr):

		self._version = (0, 0, 0)
		self._release = ("", 0)
		self._build = 0

		self.__parse(verStr)
	
	def __repr__(self):
		if not self._release[0] == "":
			if self._release[1] > 0:
				release = "%s%d" % self._release
			else:
				release = release[0]
		else:
			release = ""

		return "<version %s%s-%d>" % (\
				string.join([str(x) for x in self._version], "."), \
				release, self._build)

	def __eq__(self, y):
		c1 = reduce(lambda a, b: a and b, \
				map(lambda a, b: a == b, self._version, y._version))
		c2 = self._release == y._release
		c3 = self._build == y._build
		return c1 and c2 and c3
	
	def __ne__(self, y):
		return not self == y

	def __gt__(self, y):
		eq = map(lambda a, b: a == b, self._version, y._version)
		gt = map(lambda a, b: a > b, self._version, y._version)
		for i, t in enumerate(gt):
			if t and reduce(lambda a, b: a and b, eq[0:i], True):
				return True
		if reduce(lambda a, b: a and b, eq):
			if (self._release[0] > y._release[0]) and \
					self._release[1] > y._release[1]:
						return True
			if self._build > y._build:
				return True
		return False

	def __lt__(self, y):
		return not self > y

	def __convert(self, i, m):

		if i == 0:

			version = m.group(1)
			release = m.group(2)
			releaseNo = m.group(3)
			build = m.group(4)

			self._version = [int(x) for x in version.split(".")]

			if release is not None:
				if releaseNo is not None:
					self._release = (release, int(releaseNo))
				else:
					self._release = (release, 0)

			if build is not None:
				self._build = int(build)

		elif i == 1:
			version = m.group(1)
			self._version = [int(x) for x in version.split("_")]

	def __parse(self, s):
		try:
			for i, format in enumerate(FORMATS):
				m = re.match(format, s)
				if m is not None:
					self.__convert(i, m)
		except Exception, e:
			raise Error("Cannot parse '%s' (%s)" % (s, e))
