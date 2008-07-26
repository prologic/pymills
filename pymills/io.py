# Filename: io.py
# Module:	io
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Advanced IO

This module contains various classes for advanced IO.
For instance, the Command class, used to make writing
command-style programs easier. (ie: programs that prompt for
input and accept commands and react to them)
"""

import os
import sys
import fcntl
import select
import inspect
import readline

from pymills.event import Component
from pymills.net.sockets import POLL_INTERVAL, BUFFER_SIZE, Read, Error

class File(file):

	def setblocking(self, flag):
		" set/clear blocking mode"
		# get the file descriptor
		fd = self.fileno()
		# get the file's current flag settings
		fl = fcntl.fcntl(fd, fcntl.F_GETFL)
		if flag:
			# clear non-blocking mode from flags
			fl = fl & ~os.O_NONBLOCK
		else:
			# set non-blocking mode from flags
			fl = fl | os.O_NONBLOCK
		# update the file's flags
		fcntl.fcntl(fd, fcntl.F_SETFL, fl)

	def write(self, str):
		try:
			return os.write(self.fileno(), str)
		except OSError, inst:
			raise IOError(inst.errno, inst.strerror, inst.filename)

class Command(object):

	HELP = 0
	QUIT = 1

	def __init__(self, help, prompt, commands,
			historyFile="$HOME/.pymills_history"):
		self.help = help
		self.prompt = prompt
		self.commands = commands

		self._historyFile = historyFile
		self.readHistory()
	
	def readHistory(self):
		readline.load_history_file(
				os.path.expandvars(self._historyFile))

	def writeHistory(self):
		readline.write_history_file(
				os.path.expandvars(self._historyFile))

	def _pos(self, command):
		for a, b in self.commands:
			if a == command:
				return self.commands.index((a, b))
		return -1
	
	def process(self):
		input = Input(True)
		s = input.read(self.prompt)
		while s is not None:
			tokens = s.split(" ")
			command = tokens[0]
			args = tokens[1:]

			pos = self._pos(command)
			if pos > -1:
				a, b = self.commands[pos]
				if inspect.isfunction(b):
					b(args)
				elif inspect.isclass(b):
					c = b(args)
					c.run()
				elif b == self.QUIT:
					sys.exit(0)
				elif b == self.HELP:
					print self.help
			else:
				print "ERROR: Invalid Command"

			s = input.read(self.prompt)

		self.writeHistory()

class Input(object):

	def __init__(self, exitOnEOF=False):
		self._exitOnEOF = exitOnEOF

	def read(self, prompt=None, default=None, expected=None):
		try:
			if prompt is not None:
				if default is not None:
					prompt = "%s [%s] " % (prompt, default)
				input = raw_input(prompt)
			else:
				input = raw_input()

			if expected is not None:
				if input in expected:
					return input
				else:
					return default
			else:
				if input == "":
					return default
				else:
					return input

		except EOFError:
			if self._exitOnEOF:
				sys.exit(0)

import select


class Stdin(Component):

	channel = "stdin"

	def __init__(self, *args, **kwargs):
		super(Stdin, self).__init__(*args, **kwargs)

		self._stdin = File("/dev/stdin", "r")
		self._stdin.setblocking(False)
		self._fds = [self._stdin]

	def poll(self, wait=POLL_INTERVAL):
		try:
			r, w, e = select.select(self._fds, [], [], wait)
		except select.error, error:
			if error[0] == 4:
				pass
			else:
				self.push(Error(error), "error", self.channel)
				return

		if r:
			data = self._stdin.read(BUFFER_SIZE)
			if data:
				self.push(Read(data), "read", self.channel)
			else:
				self.close()
				return

	def close(self):
		self._stdin.close()
		self._fds = []
