# Filename: IO.py
# Module:   IO
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""I/O Library

This I/O Library contains some usefull classes to make doing
I/O related tasks a little easier.
"""

__version__ = '0.3.1'

import sys
import string
import inspect
import readline

from utils import Tokenizer

class stdin:
	"Class to handle standard input operations"

	def __init__(self):
		"Open object with file descriptor to standard input"

		self.fd = open('/dev/stdin', 'r')
	
	def __iter__(self):
		"Use the built-in file object's iter method"

		return self.fd.__iter__()
	
	def close(self):
		"Closed the file descriptor to standard input"

		self.fd.close()
	
	def readline(self):
		"Reads and returns the next line from standard input"

		return self.fd.readline()

class stdout:
	"Class to handle standard output operations"

	def __init__(self):
		"Open object with file descriptor to standard output"

		self.fd = open('/dev/stdout', 'w')
	
	def close(self):
		"Closed the file descriptor to standard output"

		self.fd.close()
	
	def writeline(self, line):
		"Writes a line to standard output"

		self.fd.write(line)

class stderr:
	"Class to handle standard error operations"

	def __init__(self):
		"Open object with file descriptor to standard error"

		self.fd = open('/dev/stderr', 'w')
	
	def close(self):
		"Closed the file descriptor to standard error"

		self.fd.close()
	
	def writeline(self, line):
		"Writes a line to standard error"

		self.fd.write(line)

class Command:
	"Class to simplify the creation of a command-driven app"

	HELP = 0
	QUIT = 1

	def __init__(self, help, prompt, commands):
		"""Initialize Command object

		help     - help string
		prompt   - prompt string
		commands - list of tuples (command, function/object)
		           eg: [('q', quit), ('a', add)]

		The following is expected of the function or object
		passed to the commands list.

		Functions:
			def foo(args):
				pass

		Classes:
			def foo:
				def __init__(self, args):
					self.args = args
				def run(self):
					pass

		Notes:
		      To define the 'help' and 'quit' commands, use the
				built-in HELP and QUIT attributes of this class.

				eg:
				   commands = [('q', Command.QUIT)]
		"""

		self.help = help
		self.prompt = prompt
		self.commands = commands
	
	def _pos(self, command):
		for a, b in self.commands:
			if a == command:
				return self.commands.index((a, b))
		return -1
		
	def process(self):
		"Main process loop"

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
	"""ReadLine Class
	
	This class makes use of the readline module which behaves
	similar to GNU's readline function.
	
	* Input editing
	* History
	"""

	def __init__(self, ExitOnEOF = False):
		"""Initialize Object

		ExitOnEOF - (boolean) Terminate upon EOF if True
		"""

		self.ExitOnEOF = ExitOnEOF
	
	def read(self, prompt = None, default = "", expected = [], NullOk = False):
		"""Read and return input from the user

		prompt   - (string)  Prompt to display
		expected - (list)    List of expected inputs
		NullOk   - (boolean) Allow null inputs if True
		"""

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
	"""Input Class 

	This Input Class read input from the user using select to
	read from stdin in a non-blocking fashion.

	* Non-Blocking
	"""

	def __init__(self):
		"""Initialise Object

		Opens /dev/stdin which is used for input
		"""

		self.stdin = open('/dev/stdin', 'r')

	def poll(self):
		"Poll for input, Return True if input is available"

		ready = select.select([self.stdin], [], [])
		read = ready[0]
		return read != []
	
	def read(self, bufsize = 512):
		"Read and Return input at most bufsize chars"

		return self.stdin.read(bufsize)

	def readline(self):
		"Read and Return a whole line of input"

		line = self.stdin.readline()
		return line
	
	def close(self):
		"""Close Object
		
		Closes /dev/stdin
		"""

		self.stdin.close()

class Table:
	"Class to print a table list items"

	def __init__(self, headers):
		"""Initialize Table object

		'headers' - [('name', length, position)]

		position
		 -1 - left justified
		  0 - centered
		  1 - right justified

		eg:
		   table = Table([('id', 4, -1), ('name', 10, 0)])
		"""

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
		"Prints the Table header"

		print self.header
	
	def printRule(self):
		"Prints a Rule"

		print '-' * len(self.header)
		
	def printRow(self, row):
		"Print a single row in the Table"

		print string.join(map(self._convert, self.headers, row), '')

def test():
	"""Test function to perform a self-test on this library

	To run, type: python IO.py
	"""

	_stdin = stdin()
	_stdout = stdout()
	_stderr = stderr()

	for line in _stdin:
		_stdout.writeline(line)
		_stderr.writeline(line)
	
	_stdin.close()
	_stdout.close()
	_stderr.close()

	headers = [('id', 4, -1), ('Name', 10, -1), ('Age', 3, -1)]
	table = Table(headers)
	table.printHeader()
	table.printRule()
	table.printRow(['0', 'James', '21'])
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

#" vim: tabstop=3 nocindent autoindent
