# Filename: cmdopt.py
# Module:   cmdopt
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate$
# $Author$
# $Id$

"""Command-line Options module."""

import os
import sys
import getopt

class Error(Exception):
	pass

class CmdOpt:

	def __init__(self, short, long):
		self._options = []
		self._arguments = []

		try:
			self._options, self._arguments = \
					getopt.gnu_getopt(sys.argv[1:], short, long)
		except getopt.GetoptError, e:
			raise Error("Could not read options!")

	def empty(self):
		return self._options == [] and self._arguments == []
	
	def getOptions(self):
		return _Options(self._options)

	def getArguments(self):
		return self._arguments

class _Options:

	def __init__(self, options):
		self._options = {}

		for option, value in options:
			self._options[option] = value

	def __contains__(self, option):
		short, long = option
		return short in self._options or long in self._options

	def __getitem__(self, option):
		short, long = option
		if short in self._options:
			return self._options[short]
		elif long in self._options:
			return self._options[long]
		else:
			raise Error("OptionError: '%s' is not an option.")
