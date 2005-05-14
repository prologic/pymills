# Filename: cmdopt.py
# Module:   cmdopt
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-08 21:16:31 +1000 (Fri, 08 Apr 2005) $
# $Author: prologic $
# $Id: cmdopt.py 1572 2005-04-08 11:16:31Z prologic $

"""Command-line Options module."""

import os
import sys
import getopt

class Error(Exception):
	pass

class CmdOpt:

	def __init__(self, short, long, usage, allowEmpty=True):
		self._usage = usage
		self._options = []
		self._arguments = []

		try:
			self._options, self._arguments = \
					getopt.gnu_getopt(sys.argv[1:], short, long)
		except getopt.GetoptError, e:
			raise Error("Could not read options!")

		if not allowEmpty and self.empty():
			self.displayUsage()
			sys.exit(0)

	def empty(self):
		return self._options == [] and self._arguments == []
	
	def displayUsage(self):
		sys.stdout.write("%s\n" % self._usage)
		sys.stdout.flush()
	
	def getOptions(self):
		return _Options(self._options)

	def getArguments(self):
		return self._arguments

class _Options:

	def __init__(self, options):
		self._options = []

		for short, long in options:
			if not short == "":
				self._options.append(short)
			if not long == "":
				self._options.append(long)

	def __contains__(self, option):
		short, long = option
		return short in self._options or long in self._options

	def __getitem__(self, n):
		return self._options[n]
