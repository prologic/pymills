# Filename: CmdOpt.py
# Module:   CmdOpt
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-08 21:16:31 +1000 (Fri, 08 Apr 2005) $
# $Author: prologic $
# $Id: CmdOpt.py 1572 2005-04-08 11:16:31Z prologic $

"""CmdOpt

This is the Command-line Options Class used to parse and use
command line options and arguments in your pgoram.
"""
import getopt, sys

class CmdOpt:
	"Class to parse and handle Command-line Options and Arguments"

	def __init__(self, short, long, usage, NullArgs = True, Errors = True):
		"""Initialize object

		short - string of short options -> 'hsa:b:'
		long  - list of long options -> ['--help', '--foo']
		usage - usage (help) string

		NullArgs
			Allows no command line arguments if True

		Errors
			Aborts on errors if True
		"""

		self.usageStr = usage
		self.opts = []
		self.args = []
		try:
			self.opts, self.args = getopt.gnu_getopt(sys.argv[1:], short, long)
		except getopt.GetoptError, e:
			if Errors:
				print 'ERROR:', e
				sys.exit(2)

		if not NullArgs and self.empty():
			self.usage()
			sys.exit(1)

	def empty(self):
		"Returns True if no options or arguments"

		return self.opts == [] and self.args == []
	
	def usage(self):
		"Prints the usage string"

		print self.usageStr
	
	def options(self):
		"Returns an Options object"

		return Options(self.opts)

class Options:
	"Class to handle Command-line Ooptions and their Values"

	def __init__(self, optlist):
		self.options = []
		self.values = []
		for opt, val in optlist:
			self.options.append(opt)
			self.values.append(val)

	def _pos(self, option):
		"Returns the position of the option"

		return self.options.index(option)

	def _which(self, option):
		"""Returns:

		0  - short option
		1  - long option
		-1 - non-existant option
		"""

		if option[0] in self.options:
			return 0
		elif option[1] in self.options:
			return 1
		else:
			return -1
	
	def has(self, option):
		"Returns True if 'option' exists"

		return not self._which(option) == -1
	
	def get(self, option, default = None):
		"Returns the value of the options, default if non-existant"

		if self.has(option):
			return self.values[self._pos(option[self._which(option)])]
		else:
			return default

#" vim: tabstop=3 nocindent autoindent
