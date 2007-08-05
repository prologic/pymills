# Filename: timers.py
# Module:	timers
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Timers

This is a module that allows you to implement timed-events
in your running application/process.
"""

from time import time

from event import Event, Component

class TimerEvent(Event):

	def __init__(self, n, **kwargs):
		Event.__init__(self, n, **kwargs)

class Timers(Component):
	"""Timers(event) -> new timers component

	Creates a new timer component that allows you to add
	timed-events which will fire a "timer" event when
	they are triggered.
	"""

	def __init__(self, *args):
		"initializes x; see x.__class__.__doc__ for signature"

		self._timers = []
	
	def find(self, **kwargs):
		for i, timer in enumerate(self._timers):
			found = True
			for k, v in kwargs.iteritems():
				try:
					if not timer._kwargs[k] == v:
						found = False
						break
				except KeyError:
					foudn = False
			if found:
				return i

	def remove(self, x):
		"""T.remove(x) -> None

		Remove the x'th timer in the list.
		"""

		del self._timers[x]

	def add(self, n, channel="timer", forever=False,
			initial=False, **kwargs):
		"""T.add(n, channel="timer", forever=False,
		      initial=False, **kwargs) -> None

		Add a new event to be timed and triggered of length
		n seconds. By default this will add the event to
		the "timer" channel and is a once-only timer unless
		forever is True.

		If initial=True and forever=True then this timer
		will trigger once when it's created, then wait n
		seconds before triggering again.

		Any additional data can be provided by kwargs.
		"""

		self._timers.append(
				Timer(n, channel, forever, initial, **kwargs))
	
	def process(self):
		"""T.process() -> None

		Process all current timers. If any trigger push
		a "TimerEvent" event onto the queue. Reset timers
		that are marked with the forever flag.
		"""

		for timer in self._timers[:]:
			done, event, channel = timer.process()
			if done:
				self.event.push(event, channel)
				if not timer._forever:
					self._timers.remove(timer)

class Timer:
	"""Timer(n, channel="timer", forever=False,
	      initial=False, **kwargs) -> new timer object
	
	Creates a new timer object which when triggered
	will return an event to be pushed onto the event
	queue held by the Timers container.
	"""

	def __init__(self, n, channel="timer", forever=False,
			initial=False, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		self._n = n
		self._channel = channel
		self._forever = forever
		self._initial = initial
		self._kwargs = kwargs

		self.reset()
	
	def reset(self):
		"""T.reset() -> None

		Reset the timer.
		"""

		self._etime = time() + self._n

	def process(self):
		"""T.process() -> bool, TimerEvent, str

		Check if this timer is ready to be triggered.
		If so, return (True, TimerEvent, channel), otherwise
		return (False, None, None).

		If this timer has the forever flag set to True,
		reset the timer after triggering.
		"""

		if time() > self._etime:
			if self._forever:
				self.reset()
			return True, TimerEvent(self._n, **self._kwargs), \
					self._channel
		else:
			if self._initial and self._forever:
				self._initial = False
				return True, TimerEvent(
						self._n,
						**self._kwargs), \
								self._channel
			return False, None, None
