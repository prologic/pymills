# Filename: utils.py
# Module:	utils
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Utilities

Various utility classes and functions.
"""

import os
import re
import sys
import optparse
from optparse import _match_abbrev
from ConfigParser import ConfigParser as _ConfigParser

from datatypes import CaselessDict

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

def loadConfig(filename, *paths):
	"""loadConfig(filename, *paths) -> ConfigParser object

	Load the configuration file specified by filename
	searching all the paths given by paths.
	If no configuration file could be loaded, an IOError
	exception is raised.
	"""

	from ConfigParser import ConfigParser

	conf = ConfigParser()
	files = [ \
			"/etc/%s" % filename,
			"%s/%s" % (os.getcwd(), filename),
			os.path.expanduser("~/.%s" % filename)]
	files += ["%s/%s" % (path, filename) for path in paths]
	if conf.read(files) == []:
		raise IOError("Could not read any config files. " \
				"Tried: %s" % files)
	else:
		return conf

def daemonize(stdin="/dev/null", stdout="/dev/null",
		stderr="/dev/null"):
	"""daemonize(stdin="/dev/null", stdout="/dev/null",
			stderr="/dev/null") -> None
	
	This forks the current process into a daemon.

	The stdin, stdout, and stderr arguments are file names that
	will be opened and be used to replace the standard file descriptors
	in sys.stdin, sys.stdout, and sys.stderr.

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
	os.chdir("/") 
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
	si = open(stdin, "r")
	so = open(stdout, "a+")
	se = open(stderr, "a+", 0)
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

	def __gr__(self, state):
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

		if not s in self._states:
			self._add(s)

		self._state = s

class CaselessOptionParser(optparse.OptionParser):
	"""CaselessOptionParser() -> new Caseless OptionParser object

	Create a new Caseless OptionParser object based on the
	standard OptionParser provided by the Python's Standard
	optparse Library. This allows you to have case-less
	options, 	which means that -r and -R passed to a program
	are equivilent.
	"""

	def _create_option_list(self):
		self.option_list = []
		self._short_opt = CaselessDict()
		self._long_opt = CaselessDict()
		self._long_opts = []
		self.defaults = {}

	def _match_long_opt(self, opt):
		return _match_abbrev(opt.lower(), self._long_opt.keys())

class Option(optparse.Option):
	"""Option(...) -> new Option object

	Creates a new option object based on the standard
	Option provided by the Python's Standard opparse
	Library which supports the "required" attribute.

	This means you can specify that an option required
	some value.
	"""

	ATTRS = optparse.Option.ATTRS + ["required"]

	def _check_required(self):
		if self.required and not self.takes_value():
			raise optparse.OptionError(
				"required flag set for option that doesn't take a value",
				self)

	# Make sure _check_required() is called from the constructor!
	CHECK_METHODS = optparse.Option.CHECK_METHODS + [_check_required]

	def process(self, opt, value, values, parser):
		"""O.process(opt, value, values, parser) -> None

		Process the option calling the base-classes's process
		method, then adding this option to the parser's
		option_seen dict.
		"""

		optparse.Option.process(self, opt, value, values, parser)
		parser.option_seen[self] = 1

class OptionParser(optparse.OptionParser):
	"""OptionParser() -> new OptionParser object

	Creates a new OptionParser object based on the standard
	OptionParser provided by Python's Standard optparse
	Library which implements the "required" attribute of
	options checking that all options marked with required
	are supplied.
	"""

	def _init_parsing_state(self):
		optparse.OptionParser._init_parsing_state(self)
		self.option_seen = {}

	def check_values(self, values, args):
		"""O.check_values(values, args) -> values, args

		Check that all options marked with "required" are
		supplied, return (values, args). If any options
		marked with "required" is not supplied, raise
		an error.
		"""

		for option in self.option_list:
			if (isinstance(option, Option) and
					option.required and
					not self.option_seen.has_key(option)):
				self.error("%s not supplied" % option)
		return (values, args)

def getFiles(path, tests=[os.path.isfile], pattern=".*"):
	"""getFiles(path, tests=[os.path.isfile], pattern=".*") ->
			list or []
	
	Return a list of files in the specified path
	applying the predicates listed in tests returning
	only the files that match the pattern.
	"""

	files = os.listdir(path)
	list = []
	for file in files:
		if reduce(lambda x, y: x and y, tests[1:], tests[0]) and \
				re.match(pattern, file):
					list.append(file)
	return list
	
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

def caller(n=1):
	"""caller(n=1) -> str

	Return the name of the calling function.
	If n is specified, return the n'th function
	in the stack.
	"""

	from traceback import extract_stack
	stack = extract_stack()
	return stack[-n-2][2]

def sendEmail(fromEmail, toEmail, subject, message):
	"""sendEmail(fromEmail, toEmail, subject, message) -> None

	A helper function to send an email.
	"""

	import smtplib
	from email.MIMEText import MIMEText

	msg = MIMEText(message)
	msg["Subject"] = subject
	msg["From"] = fromEmail
	msg["To"] = toEmail

	s = smtplib.SMTP()
	s.connect()
	s.sendmail(fromEmail, toEmail, msg.as_string())
	s.close()

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
			if not alreadyImported.has_key(name):
				del (sys.modules[name])

class ConfigParser(_ConfigParser):

	def get(self, section, option, *args):
		if self.has_option(section, option):
			return _ConfigParser.get(self, section, option, *args)
		else:
			return None

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

def MixIn(cls, mixin, last=False):
	if mixin not in cls.__bases__:
		if last:
			cls.__bases__ += (mixin,)
		else: 
			cls.__bases__ = (mixin,) + cls.__bases__
