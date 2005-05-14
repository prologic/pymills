# Filename: IO.py
# Module:   IO
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Input/Output Module"""

import sys
import string
import inspect
import readline

from utils import Tokenizer

class Command:

	HELP = 0
	QUIT = 1

	def __init__(self, help, prompt, commands):
		self.help = help
		self.prompt = prompt
		self.commands = commands
	
	def _pos(self, command):
		for a, b in self.commands:
			if a == command:
				return self.commands.index((a, b))
		return -1
		
	def process(self):
		input = Input(True)
		s = input.read(self.prompt, [], True)
		while  not s == '':
			tokens = Tokenizer(s)
			command = tokens.next()
			args = tokens.rest()

			pos = self._pos(command)
			if pos > -1:
				(a, b) = self.commands[pos]
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
				print 'ERROR: Invalid Command'

			s = input.read(self.prompt, [], True)

class Input:

	def __init__(self, ExitOnEOF = False):
		self.ExitOnEOF = ExitOnEOF
	
	def read(self, prompt = None, default = "", expected = [], NullOk = False):
		try:
			if prompt:
				if default:
					prompt = prompt + " [" + default + "] "
				input = raw_input(prompt)
			else:
				input = raw_input()

			if not expected == []:
				if input in expected:
					return input
				else:
					if not NullOk:
						return None
					elif input == '':
						return input
					else:
						return None
			else:
				if input == '' and NullOk:
					return default
				elif not NullOk:
					if not input == '':
						return input
					else:
						return None
				else:
					return input

		except EOFError:
			if self.ExitOnEOF:
				sys.exit(0)

class SelectInput:

	def __init__(self):
		self._stdin = sys.stdin

	def poll(self):
		ready = select.select([self._stdin], [], [])
		read = ready[0]
		return read != []
	
	def read(self, bufsize=512):
		return self._stdin.read(bufsize)

	def readline(self):
		line = self._stdin.readline()
		return line
	
class Table:

	def __init__(self, headers):
		self.headers = headers

		self.header = ''
		for header in headers:
			if header[2] == -1:
				self.header = self.header + header[0].ljust(header[1])
			elif header[2] == 0:
				self.header = self.header + header[0].center(header[1])
			elif header[2] == 1:
				self.header = self.header + header[0].rjust(header[1])

	def _convert(self, header, value):
		if header[2] == -1:
			return value.ljust(header[1])
		elif header[2] == 0:
			return value.center(header[1])
		elif header[2] == 1:
			return value.rjust(header[1])
		
	def printHeader(self):
		print self.header
	
	def printRule(self):
		print '-' * len(self.header)
		
	def printRow(self, row):
		print string.join(map(self._convert, self.headers, row), '')
