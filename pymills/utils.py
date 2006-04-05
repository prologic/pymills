# Filename: utils.py
# Module:	utils
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Utilities

Various utility classes and functions
"""

import os
import re
import sys
import string
import random

class Error(Exception):
	pass

def getProgName():
	return os.path.basename(sys.argv[0])

def writePID(file):
	try:
		fd = open(file, "w")
		fd.write(str(os.getpid()))
		fd.close()
	except Exception, e:
		raise Error("Error writing pid to %s: %s" % (file, e))

def loadConfig(filename, *paths):
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

	def __init__(self):
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
		if self._states.has_key(state):
			self._state = state
		else:
			self._add(state)
			self._state = state

class Tokenizer(list):

	def __init__(self, str, delim=" "):
		self._delim = delim
		list.__init__(self, str.split(delim))

	def peek(self, n=0):
		if not self == [] and (0 <= n < len(self)):
			return self[n]
		else:
			return None

	def next(self):
		if not self == []:
			return self.pop(0)
		else:
			return None
	
	def last(self):
		if not self == []:
			return self.pop()
		else:
			return None
	
	def copy(self, s, e=None):
		if e is not None:
			return string.join(self[s:], self._delim)
		else:
			return string.join(self[s:e], self._delim)

	def delete(self, n):
		if 0 <= n < len(self):
			del self[n]
	
	def has(self, token):
		return token in self

	def more(self):
		return not self == []

	def rest(self):
		return string.join(self, self._delim)

def getFiles(path, tests=[os.path.isfile], pattern=".*"):
	files = os.listdir(path)
	list = []
	for file in files:
		if reduce(lambda x, y: x and y, tests[1:], tests[0]) and \
				re.match(pattern, file):
					list.append(file)
	return list
	
def isReadable(file):
	return os.access(file, os.R_OK)

def mkpasswd(n):
	validCharacters = string.ascii_lowercase + string.digits
	validCharacters = validCharacters.strip("oO0")
	return string.join(
			[random.choice(validCharacters)
				for x in range(n)], "")

def caller(n=1):
	from traceback import extract_stack
	stack = extract_stack()
	return stack[-n-2][2]

def sendEmail(fromEmail, toEmail, subject, message):
	import smtplib
	from email.MIMEText import MIMEText
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg["From"] = fromEmail
	msg["To"] = toEmail
	s = smtplib.SMTP()
	s.connect()
	s.sendmail(fromEmail, toEmail, msg.as_string())
	s.close()
