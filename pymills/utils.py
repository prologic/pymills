# Filename: utils.py
# Module:   utils
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-24 14:23:46 +1000 (Sun, 24 Apr 2005) $
# $Author: prologic $
# $Id: utils.py 1759 2005-04-24 04:23:46Z prologic $

"""Utility Module

This module contains various utility functions and classes to
help make writing certain aspects of a program easier.
"""

import os
import sys
import string

class Error(Exception):
	"""Error Class

	Used to raise exceptions upon erors
	"""

	pass

def getProgName():
	"""Returns the current name of the running program
	
	Args:
	   None
	
	Returns:
	   string (containing the name of the runnning program)
	"""

	return os.path.splitext(os.path.basename(sys.argv[0]))[0]

def writePID(file):
	"""Writes the pid of current process to a file
	
	Given file, this will write the current PID (process id) of
	the currently running program into the file given by file.
	
	Args:
	   file : string of the filename to write to
	
	Returns:
	   None
	"""

	try:
		fd = open(file, "w")
		fd.write(str(os.getpid()))
		fd.close()
	except Exception, e:
		raise Error("Error writing pid to %s: %s" % (file, e))

def loadConfig():
	"""Load the program's configuration

	Given an environment, this will attempt to look for a
	configuration file (usually conf.py) in some standard
	locations and load it.

	Args:
	   None

	Returns:
	   True or False
	"""

	curDir = os.getcwd()
	homeDir = os.path.expanduser("~") 
	etcDir = "/etc/"

	paths = [
		curDir,
		"%s/.%s" % (homeDir, getProgName()),
		"%s/%s" % (etcDir, getProgName())]

	for path in paths:
		if os.path.isdir(path):
			sys.path.append(path)
			if __import__("conf", dict) is not None:
				return True
			else:
				sys.path.remove(path)

	return False

def daemonize(stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"):
	"""This forks the current process into a daemon.

	The stdin, stdout, and stderr arguments are file names that
	will be opened and be used to replace the standard file descriptors
	in sys.stdin, sys.stdout, and sys.stderr.

	Example:
	   if __name__ == "__main__":
	      daemonize('/dev/null','/tmp/daemon.log','/tmp/daemon.log')
	      main()

	Args:
	   stdin : file to write standard input to
	   stdout : file to write standard output to
	   stderr : file to write standard error to
	
	These arguments are optional and default to /dev/null.

	Note that stderr is opened unbuffered, so
	if it shares a file with stdout then interleaved output
	may not appear in the order that you expect.
	
	Returns:
	   None
	"""

	# Do first fork.
	try: 
		pid = os.fork() 
		if pid > 0:
			# Exit first parent
			sys.exit(0)
	except OSError, e: 
		sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
		sys.exit(1)

	# Decouple from parent environment.
	os.chdir("/") 
	os.umask(077) 
	os.setsid() 

	# Do second fork.
	try: 
		pid = os.fork() 
		if pid > 0:
			# Exit second parent
			sys.exit(0)
	except OSError, e: 
		sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
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
	"""Class to maintain the the state of something

	Example:
	>>> from pymills import utils
	>>> state = utils.State()
	>>> state

	>>> state.set("START")
	>>> state
	START
	>>> state.set("S1")
	>>> state
	S1
	>>> state == "S1"    
	True
	"""

	def __init__(self):
		"""Initialize"""

		self._states = {}
		self._nextValue = 0

		# Default States

		self._add("START")
		self._add("DONE")

	def __repr__(self):
		try:
			return self._state
		except AttributeError:
			return ""

	def __str__(self):
		try:
			return self._state
		except AttributeError:
			return ""
	
	def __eq__(self, state):
		if self._states.has_key(state):
			return self._state == state
		else:
			return False
	
	def _add(self, state):
		self._states[state] = self._nextValue
		self._nextValue = self._nextValue + 1
	
	def set(self, state):
		"""Set the state

		Given a new state, set the state if such a state exists
		in the set of possible states, otherwise add it first,
		then set the state.

		Args:
		   state : string to set the state to

		Returns:
		   None
		"""

		if self._states.has_key(state):
			self._state = state
		else:
			self._add(state)
			self._state = state

class Tokenizer(list):
	"""Tokenizer Class

	Class to split a string into tokens with many different
	supporting methods such as: index, last, peek, more, next
	and more...

	Example:
	>>> from pymills import utils
	>>> tokens = utils.Tokenizer("foo bar 1 2 3")
	>>> tokens[0]
	'foo'
	>>> tokens.last()
	'3'
	>>> tokens.peek()
	'foo'
	>>> tokens.next()
	'foo'
	>>> tokens.more()
	True
	"""

	def __init__(self, str, delim=" "):
		"""Initialize class

		Given a string str and an optional delim setup this
		class. The delim parameter is optional and is by default
		set to " ", ie: a string of tokens seperated with spaces.

		Args:
		   str : string of the string to be tokenized
		   delim : string of the delimiter of the tokens in
		                  the string (optional)
		"""

		self._delim = delim
		tokens = string.split(str, delim)
		list.__init__(self, tokens)

	def peek(self, n=0):
		"""Return the next token but don't remove it

		This function given n will return the n'th token in the
		list but will not remove it.

		Args:
		   n : int -> 0 <= n < len(self)
			(The n'th token)

		Returns:
		   string or None
		"""

		if not self == [] and (0 <= n < len(self)):
			return self[n]
		else:
			return None

	def next(self):
		"""Return the next token and remove it

		Args:
		   None

		Returns:
		   string or None
		"""

		if not self == []:
			return self.pop(0)
		else:
			return None
	
	def last(self):
		"""Return the last token and remove it

		Args:
		   None

		Returns:
		   string or None
		"""

		if not self == []:
			return self.pop()
		else:
			return None
	
	def copy(self, s, e=None):
		"""Copy a set of tokens

		Given s and e this will return those tokens joined
		together with the original delimiter.

		Args:
		   s : int -> 0 <= s < len(self)
		      (Starting position)
		   e : int -> 0 <= e < len(self)
		      (Ending position) - optional

		Returns:
		   string
		"""

		if e is not None:
			return string.join(self[s:e], self._delim)
		else:
			return string.join(self[s:], self._delim)

	def delete(self, n):
		if 0 <= n < len(self):
			del self[n]
	
	def has(self, token):
		return token in self

	def more(self):
		return not self == []

	def rest(self):
		return string.join(self, self._delim)
