# Module:	utils
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Utilities

Various utility classes and functions.
"""

import os
import re
import sys
from os.path import isfile


class Error(Exception):
	"Error Exception"


def getProgName():
	"""getProgName() -> str

	Return the name of the current program being run
	by working it out from the script's basename.
	"""

	return os.path.basename(sys.argv[0])


def writePID(file):
	"""writePID(file) -> None

	Write the process-id of the currently running process
	to the specified file. If an error occurs, Error is
	raised.
	"""

	try:
		fd = open(file, "w")
		fd.write(str(os.getpid()))
		fd.close()
	except Exception, e:
		raise Error("Error writing pid to %s: %s" % (file, e))


def daemonize(stdin="/dev/null", stdout="/dev/null",
		stderr="/dev/null", path="/"):
	"""daemonize(stdin="/dev/null", stdout="/dev/null",
			stderr="/dev/null", path="/") -> None

	This forks the current process into a daemon.

	The stdin, stdout, and stderr arguments are file names that
	will be opened and be used to replace the standard file descriptors
	in sys.stdin, sys.stdout, and sys.stderr. The path argument is
	used to jail the process into the given path, defaults to /

	Example:
	{{{
	#!python
	if __name__ == "__main__":
		daemonize("/dev/null", "/tmp/daemon.log",
			"/tmp/daemon.log")
		main()
	}}}

	Args:
		stdin  : file to write standard input
		stdout : file to write standard output
		stderr : file to write standard error

	These arguments are optional and default to /dev/null.

	Note that stderr is opened unbuffered, so
	if it shares a file with stdout then interleaved output
	may not appear in the order that you expect.
	"""

	# Do first fork.
	try:
		pid = os.fork()
		if pid > 0:
			# Exit first parent
			raise SystemExit, 0
	except OSError, e:
		print >> sys.stderr, "fork #1 failed: (%d) %s\n" % (
				e.errno, e.strerror)
		raise SystemExit, 1

	# Decouple from parent environment.
	os.chdir(path)
	os.umask(077)
	os.setsid()

	# Do second fork.
	try:
		pid = os.fork()
		if pid > 0:
			# Exit second parent
			raise SystemExit, 0
	except OSError, e:
		print >> sys.stderr, "fork #2 failed: (%d) %s\n" % (
				e.errno, e.strerror)
		raise SystemExit, 1

	# Now I am a daemon!

	# Redirect standard file descriptors.
	si = open(os.path.abspath(os.path.expanduser(stdin)), "r")
	so = open(os.path.abspath(os.path.expanduser(stdout)), "a+")
	se = open(os.path.abspath(os.path.expanduser(stderr)), "a+", 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())


class State(object):
	"""State() -> new state object

	Creates a new state object that is suitable
	for holding different states of an application.
	Usefull in state-machines.

	The way this works is rather simple. You create a new
	state object, and simply set the state. If the state
	doesn't exist, it's added to it's internal data
	structure. The reason this is done is so that
	comparing states is consistent, and you can't just
	compare with a non-existent state.
	"""

	def __init__(self):
		"initializes x; see x.__class__.__doc__ for signature"

		self._states = {}
		self._next = 0

		# Default States

		self._add("START")
		self._add("DONE")

	def __repr__(self):
		try:
			return "<State: %s>" % self._state
		except AttributeError:
			return "<State: ???>"

	def __str__(self):
		return self._state

	def __eq__(self, s):
		return s in self._states and self._state == s

	def __lt__(self, s):
		return s in self._states and self._state == s and \
				self._states[s] < self._states[self._state]

	def __gr__(self, s):
		return s in self._states and self._state == s and \
				self._states[s] > self._states[self._state]

	def _add(self, s):
		self._states[s] = self._next
		self._next = self._next + 1

	def set(self, s):
		"""S.set(s) -> None

		Set the current state to the specified state given by s,
		adding it if it doesn't exist.
		"""

		if s not in self._states:
			self._add(s)

		self._state = s


def getFiles(root, pattern=".*", tests=[isfile], **kwargs):
	"""getFiles(root, pattern=".*", tests=[isfile], **kwargs) -> list of files

	Return a list of files in the specified path (root)
	applying the predicates listed in tests returning
	only the files that match the pattern. Some optional
	kwargs can be specified:
	 * full=True		(Return full paths)
	 * recursive=True	(Recursive mode)
	"""

	def test(file, tests):
		for test in tests:
			if not test(file):
				return False
		return True

	full = kwargs.get("full", False)
	recursive = kwargs.get("recursive", False)

	files = []

	for file in os.listdir(root):
		path = os.path.abspath(os.path.join(root, file))
		if os.path.isdir(path):
			if recursive:
				files.extend(getFiles(path, pattern, **kwargs))
		elif test(path, tests) and re.match(pattern, path):
			if full:
				files.append(path)
			else:
				files.append(file)

	return files


def isReadable(file):
	"""isReadable(file) -> bool

	Return True if the specified file is readable, False
	otherwise.
	"""

	return os.access(file, os.R_OK)


def mkpasswd(n):
	"""mkpasswd(n) -> str

	Create a random password with the specified length, n.
	"""

	import string
	import random

	validCharacters = string.ascii_letters + string.digits
	validCharacters = validCharacters.strip("oO0")
	return string.join(
			[random.choice(validCharacters)
				for x in range(n)], "")


def validateEmail(email):
	"""validateEmail(email) -> bool

	Return True if the specified email is valid, False
	otehrwise.
	"""

	return len(email) > 7 and \
			re.match(
					"^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\."
					"([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
					email) is not None


def safe__import__(moduleName, globals=globals(),
		locals=locals(), fromlist=[]):
	"""Safe imports: rollback after a failed import.

	Initially inspired from the RollbackImporter in PyUnit,
	but it's now much simpler and works better for our needs.

	See http://pyunit.sourceforge.net/notes/reloading.html
	"""

	alreadyImported = sys.modules.copy()
	try:
		return __import__(moduleName, globals, locals, fromlist)
	except Exception, e:
		raise
		for name in sys.modules.copy():
			if not name in alreadyImported:
				del (sys.modules[name])


def notags(str):
	"Removes HTML tags from str and returns the new string"

	s = State()

	STATE_TEXT = 0
	STATE_TAG = 1

	state = STATE_TEXT

	newStr = ""

	for char in str:

		if state == STATE_TEXT:
			if char == '<':
				state = STATE_TAG
			else:
				newStr = newStr + char

		elif state == STATE_TAG:
			if char == '>':
				state = STATE_TEXT

	return newStr

class MemoryStats(object):

	scale = {"KB": 1024.0, "MB": 1024.0 * 1024.0}

	def __init__(self, pid=os.getpid()):
		self.filename = "/proc/%d/status" % pid

	def __getitem__(self, k):
		try:
			t = open(self.filename, "r")
			v = t.read()
			t.close()
		except:
			return 0.0
		i = v.index(k)
		v = v[i:].split(None, 3)
		if len(v) < 3:
			return 0.0
		return float(v[1]) * self.scale[v[2].upper()]

	def __call__(self):
		return self["VmSize"], self["VmRSS"], self["VmStk"]

	@property
	def size(self):
		return self["VmSize"]
	
	@property
	def rss(self):
		return self["VmRSS"]
	
	@property
	def stack(self):
		return self["VmStk"]
		
def memory(since=0.0):
	"Return memory usage in bytes."

	return MemoryStats().size - since


def resident(since=0.0):
	"Return resident memory usage in bytes."

	return MemoryStats().rss - since


def stacksize(since=0.0):
	"Return stack size in bytes."

	return MemoryStats().stack - since

def MixIn(cls, mixin, last=False):
	if mixin not in cls.__bases__:
		if last:
			cls.__bases__ += tuple([mixin])
		else:
			cls.__bases__ = tuple([mixin]) + cls.__bases__


class Cache(object):

	def __init__(self, f):
		self.f = f
		self.cache = {}

	def __call__(self, *args):
		if not args in self.cache:
			self.cache[args] = self.f(*args)
		return self.cache[args]

def printdict(d, level=0):
	"""printdict(d, level=0) -> None

	Print the given dictionary, d. Recursively
	print any nested dictionaries found. This
	function is _NOT_ a pretty printer, and
	prints a human-readable form of the given
	dictionary rather than something that can
	be re-read by Python.
	"""

	for k, v in d.iteritems():
		if type(v) == dict:
			print "%s: " % k
			printdict(v, (level + 1))
		else:
			print "%s%s: %s" % (" " * level, k, v)

def minmax(iter):
	"""minmax(iter) -> (min, max)

	Consume the interable iter and calculate and
	return the min and max of each item.
	"""

	min = max = None
	for item in iter:
		if min is None or item < min:
			min = item
		if max is None or item > max:
			max = item
	return min, max

def caller(n=1):
	"""caller(n=1) -> str

	Return the name of the calling function.
	If n is specified, return the n'th function
	in the stack.
	"""

	from traceback import extract_stack
	stack = extract_stack()
	return stack[-n-2][2]
