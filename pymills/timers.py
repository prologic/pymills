# Filename: timers.py
# Module:	timers
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Timers

This is a module that allows you to implement timed-events
in your running application/process.

Example:
from pymills.timers import Timers

def hello(name, length, args):
   print "Hello World"

timers = Timers()
timers.add("hello", 5, hello)

while True:
   timers.run()
"""

import time

class Timers:

	def __init__(self):
		self._timers = []
	
	def add(self, name, length, function, forever=False, *args):
		self._timers.append(_Timer(name, length, function, forever, args))
	
	def run(self):
		for i, timer in enumerate(self._timers[:]):
			if timer.run():
				if not timer.forever:
					del self._timers[i]
				else:
					timer.reset()

class _Timer:

	def __init__(self, name, length, function, forever, args):
		self._name = name
		self._length = length
		self._function = function
		self.forever = forever
		self._args = args

		self.reset()
	
	def reset(self):
		self._start = time.time()

	def run(self):
		if (time.time() - self._start) >= self._length:
			self._function(self._name, self._length, self._args)
			return True
		else:
			return False
