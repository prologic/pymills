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
import inspect
import readline
import select

class Command:

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

class Input:

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

class SelectInput:

	def __init__(self):
		self._stdin = sys.stdin

	def poll(self, wait=0.01):
		ready = select.select([self._stdin], [], [], wait)
		read = ready[0]
		return read != []

	def read(self, bufsize=512):
		return self._stdin.read(bufsize)

	def readline(self):
		line = self._stdin.readline()
		return line

class Table:
	"""Class to print nicely formatted tables

	This class will allow you to print nice pretty
	tabl-like outputs to stdout. You give it a header
	and add a bunch of rows, then print it.
	"""

	LEFT = -1
	CENTER = 0
	RIGHT = 1

	def __init__(self, headers):
		"""Initialize Table Object

		Syntax of headers (list of tuples):
		(title, length, justify)
		"""

		self._headers = headers
		self._header = ""
		self._rows = []

		for title, length, justify in headers:
			if justify == Table.LEFT:
				self._header += title.ljust(length)
			elif justify == Table.CENTER:
				self._header += title.center(length)
			elif justify == Table.RIGHT:
				self._header += title.rjust(length)
			else:
				self._header += title.ljust(length)

	def __str__(self):

		import string
		from StringIO import StringIO

		s = StringIO()
		s.write("%s\n" % self._header)
		s.write("-" * len(self._header))
		s.write("\n")

		for row in self._rows:
			s.write("%s\n" % string.join(
				map(self._convert, self._headers,
					map(str, row)), ""))

		s.write("-" * len(self._header))
		s.write("\n")

		try:
			return s.getvalue()
		finally:
			s.close()

	def _convert(self, header, value):
		length, justify = header[1:]
		if justify == Table.LEFT:
			return value.ljust(length)
		elif justify == Table.CENTER:
			return value.center(length)
		elif justify == Table.RIGHT:
			return value.rjust(length)

	def add(self, row):
		"""Adds a new row to the table

		row - list of values to print
		"""

		self._rows.append(row)

##
## Tests
##

def test():
	"""Test function to perform a self-test on this module

	To run, type: python io.py
	"""

	headers = [
		("id", 4, Table.LEFT),
		("Name", 10, Table.LEFT),
		("Age", 3, Table.LEFT)]
	table = Table(headers)
	table.add([0, "James", 21])
	print table

	help = "Help me! I'm stupid!"

	commands = []
	commands.append(("quit", Command.QUIT))
	commands.append(("help", Command.HELP))
	commands.append(("hello", hello))
	commands.append(("world", world))

	prompt = "Command: "

	command = Command(help, prompt, commands)
	command.process()

def hello(args):
	print "Hello"
	print args

class world:
	def __init__(self, args):
		self.args = args
	def run(self):
		print "World"
		print self.args

if __name__ == "__main__":
	test()
