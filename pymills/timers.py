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

from event import *

class TimerEvent(Event):

	def __init__(self, name, length, callable, forever,
			*args, **kwargs):
		Event.__ini__(self,
				name, length, callable, forever,
				*args, **kwargs)

class Timers(Component):

	def __init__(self, *args):
		self._timers = []
	
	@listener("timer")
	def onTIMER(self, event, name, length, callable, forever,
			*args, **kwargs):
		pass
	
	def add(self, name, length, callable=None, forever=False,
			*args, **kwargs):
		self._timers.append(
				Timer(
					name, length, callable, forever,
					*args, **kwargs))
	
	def run(self):
		for i, timer in enumerate(self._timers[:]):
			done, event = timer.run()
			if done:
				if self._event is not None:
					self._event.push(event, self._channel, timer)
				if not timer.forever:
					del self._timers[i]
				else:
					timer.reset()

class Timer:

	def __init__(self, name, length, callable, forever=False,
		*args, **kwargs):
		self._name = name
		self._length = length
		self.forever = forever
		self._callable = callable
		self._args = args
		self._kwargs = kwargs

		self.reset()
	
	def reset(self):
		self._start = time.time()

	def run(self):
		if (time.time() - self._start) >= self._length:
			if callable(self._callable):
				self._callable(self._name, self._length,
					*self._args, **self._kwargs)
			return True, TimerEvent(
					self._name,
					self._length,
					self._callable,
					*self._args,
					**self._kwargs)
		else:
			return False, None
