#!/usr/bin/env python

# Filename: Utils.py
# Module:   Utils
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-24 14:23:46 +1000 (Sun, 24 Apr 2005) $
# $Author: prologic $
# $Id: Utils.py 1759 2005-04-24 04:23:46Z prologic $

"""Utils

Utility Module
"""

__version__ = "0.1.0"
__author__ = "James Mills"
__email__ = "%s <prologic@shortcircuit.net.au>" % __author__
__copyright__ = "CopyRight (C) 2005 by %s" % __author__
__url__ = "http://shortcircuit.net.au/~prologic/"

import sys, os
from Tokenizer import Tokenizer

def getProgName():
	"Returns the current name of the running program"

	tokens = Tokenizer(sys.argv[0], '/')
	prog = tokens.last()
	return prog.split('.')[0]

def writePID(file):
	"Writes a pid of current process to file"

	fd = open(file, "w")
	fd.write(str(os.getpid()))
	fd.close()

def importModule(module, dict, quiet = True):
	"""Import Function to import dynamic modules
	
	module - module to import
	dict   - symbol table to append to

	Returns:
	<module 'module' (built-in)>
	"""

	try:
		mod = __import__(module)
		dict[module] = mod
		return mod
	except ImportError, e:
		if not quiet:
			print "ERROR: " + str(e)
		return None

def loadConfig(dict):
	"""Load the program's configuration

	dict - symbol table to append to

	Returns:
	(boolean) - True if successfully loaded.
	"""

	homeDir = os.path.expanduser("~") 
	etcDir = "/etc/"
	curDir = os.getcwd()

	#Try to load the current directory's configuration
	path = curDir
	if os.path.isdir(path):
		sys.path.append(path)
		if not importModule("conf", dict) == None:
			return True
		else:
			sys.path.remove(path)

	#Try to load the user's configuration
	path = "%s/.%s" % (homeDir, getProgName())
	if os.path.isdir(path):
		sys.path.append(path)
		if not importModule("conf", dict) == None:
			return True
		else:
			sys.path.remove(path)

	#Try to load the global configuration
	path = "%s/%s" % (etcDir, getProgName())
	if os.path.isdir(path):
		sys.path.append(path)
		if not importModule("conf", dict) == None:
			return True
		else:
			sys.path.remove(path)
	
	#If both fail
	return False

def daemonize(stdin = "/dev/null", stdout = "/dev/null", stderr = "/dev/null"):
	"""This forks the current process into a daemon.

	The stdin, stdout, and stderr arguments are file names that
	will be opened and be used to replace the standard file descriptors
	in sys.stdin, sys.stdout, and sys.stderr.

	These arguments are optional and default to /dev/null.

	Note that stderr is opened unbuffered, so
	if it shares a file with stdout then interleaved output
	may not appear in the order that you expect.

	Example:
		if __name__ == "__main__":
			daemonize('/dev/null','/tmp/daemon.log','/tmp/daemon.log')
			main()
	"""

	# Do first fork.
	try: 
		pid = os.fork() 
		if pid > 0:
			sys.exit(0)   # Exit first parent.
	except OSError, e: 
		sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
		sys.exit(1)

	# Decouple from parent environment.
	os.chdir("/") 
	os.umask(077) 
	os.setsid() 

	# Do second fork.
	try: 
		pid = os.fork() 
		if pid > 0:
			sys.exit(0)   # Exit second parent.
	except OSError, e: 
		sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
		sys.exit(1)

	# Now I am a daemon!
    
	# Redirect standard file descriptors.
	si = open(stdin, 'r')
	so = open(stdout, 'a+')
	se = open(stderr, 'a+', 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())

class State:
	"Class to maintain the the state of something"

	def __init__(self):
		"Initialize"

		self._states = {}
		self._nextValue = 0

		# Default States

		self._add("START")
		self._add("DONE")

	def __repr__(self):
		return self._state

	def __str__(self):
		return self._state
	
	def __eq__(self, state):
		if self._states.has_key(state):
			return self._state == state
		else:
			return False
	
	def _add(self, state):
		self._states[state] = self._nextValue
		self._nextValue = self._nextValue + 1
	
	def set(self, state):
		if self._states.has_key(state):
			self._state = state
		else:
			self._add(state)
			self._state = state

#vim: tabstop=3 nocindent autoindent
