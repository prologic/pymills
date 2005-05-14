# Filename: timers.py
# Module:   timers
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate$
# $Author$
# $Id$

"""Timers Module"""

import time

class Timers:

	def __init__(self):
		self._timers = []
	
	def add(self, name, length, function, *args):
		self._timers.append(_Timer(name, length, function, args))
	
	def run(self):
		for i, timer in enumerate(self._timers[:]):
			if timer.run():
				del self._timers[i]

class _Timer:

	def __init__(self, name, length, function, args):
		self._name = name
		self._length = length
		self._function = function
		self._args = args

		self._start = time.time()
	
	def run(self):
		if (time.time() - self._start) >= self._length:
			self._function(self._name, self._length, self._args)
			return True
		else:
			return False
