# Filename: cmdopt.py
# Module:   cmdopt
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-08 21:16:31 +1000 (Fri, 08 Apr 2005) $
# $Author: prologic $
# $Id: cmdopt.py 1572 2005-04-08 11:16:31Z prologic $

"""Command-line Options module.

This module provides an interface to accessing the command-line
arguments and options given to a program.

Example:
usage = "foo -h -a <x> <file>"
short ="ha-"
long = ["help", "add"]

cmdopt = CmdOpt(short, long, usage)

opts = cmdopt.getOptions()
args = cmdopt.getArguments()

if ("-l", "--help") in opts:
	print "help"

print args[0]
"""

import os
import sys
import getopt

class Error(Exception):
	"""Error Class

	Used to raise exceptions upon erors
	"""

	pass

class CmdOpt:
	"""cmdopt Class - Interface to program options and arguments.

	This class parses the command-line options and arguments
	given to a program and returns an interface to these.
	"""

	def __init__(self, short, long, usage, allowEmpty=True):
		"""Initialize

		Parse the command-line options and arguments, raise an
		exception if some oerror occurs. Display the usage if
		there were no options specified and allowEmpty = False

		Args:
		   short : string of short options
		   long : list of strings containing the long options
		   usage : string of the usage
		   allowEmpty : bool allow null arguments ?
		"""

		self._usage = usage
		self._options = []
		self._arguments = []

		try:
			self._options, self._arguments = \
					getopt.gnu_getopt(sys.argv[1:], short, long)
		except getopt.GetoptError, e:
			raise Error("Could not options!")

		if not allowEmpty and self.empty():
			self.displayUsage()
			sys.exit(0)

	def empty(self):
		"""Returns True if no options or arguments

		Args:
		   None

		Return:
		   True of False
		"""

		return self._options == [] and self._arguments == []
	
	def displayUsage(self):
		"""Prints the usage string

		Args:
		   None

		Return:
		   None
		"""

		sys.stdout.write("%s\n" % self._usage)
		sys.stdout.flush()
	
	def getOptions(self):
		"""Returns the program options
		
		Return an instance to an Options class
		
		Args:
		   None
		
		Returns:
		   Object (instance of _Options)
		"""

		return _Options(self._options)

	def getArguments(self):
		"""Return the program arguments

		Args:
		   None

		Returns:
		   list
		"""

		return self._arguments

class _Options:
	"""Class to hold program options
	
	Provides a nice interface to the program options
	This is used internally.
	"""

	def __init__(self, options):
		"""Initialize

		Args:
		   options : list of tuples
		"""

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
