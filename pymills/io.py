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
		s = input.read(self.prompt)
		while  s is not None:
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

			s = input.read(self.prompt)

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
			return str(value).ljust(header[1])
		elif header[2] == 0:
			return str(value).center(header[1])
		elif header[2] == 1:
			return str(value).rjust(header[1])
		
	def printHeader(self):
		print self.header
	
	def printRule(self):
		print '-' * len(self.header)
		
	def printRow(self, row):
		print string.join(map(self._convert, self.headers, row), '')

def test():
	"""Test function to perform a self-test on this module

	To run, type: python io.py
	"""

	headers = [
		('id', 4, -1),
		('Name', 10, -1),
		('Age', 3, -1)]
	table = Table(headers)
	table.printHeader()
	table.printRule()
	table.printRow([0, 'James', 21])
	table.printRule()

	help = "Help me! I'm stupid!"

	commands = []
	commands.append(('quit', Command.QUIT))
	commands.append(('help', Command.HELP))
	commands.append(('hello', hello))
	commands.append(('world', world))

	prompt = 'Command: '

	command = Command(help, prompt, commands)
	command.process()

def hello(args):
	print 'Hello'
	print args

class world:
	def __init__(self, args):
		self.args = args
	def run(self):
		print 'World'
		print self.args

if __name__ == '__main__':
	test()
