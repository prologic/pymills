# Module:	timers
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Timers

Timers component to facilitate timed eventd.
"""

from time import time

from pymills.event.core import Component


class Timers(Component):
	"""Timers(manager) -> new timers component

	Creates a new timers component that allows you to add
	timed-events which will fire a "Timer" event when
	they are triggered.
	"""

	timers = []

	def __len__(self):
		"T.__len__() <==> len(T)"

		return len(self.timers)

	def __getitem__(self, y):
		"T.__getitem__(y) <==> T[y]"

		return self.timers[y]

	def __delitem__(self, y):
		"T.__delitem__(y) <==> del T[y]"

		del self.timers[y]

	def remove(self, timer):
		"T.remove(timer) -- remove first occurrence of timer"

		self.timers.remove(timer)

	def add(self, s, e, c="timer", t=None, persist=False, start=False):
		"""T.add(s, e, c="timer", t=None, persist=False, start=False) -> None

		Add a new event (e) to be timed and triggered after (s)
		seconds to the specified channel (c) and target (t).
		Default channel is "timer" and target None. If persist
		is True, the timer will be persistent and run indefinately.
		If start is True, the timer will trigger before the next
		cycle, but only if perist is also True (as this only makes
		sense in persistent timers).
		"""

		self.timers.append(Timer(s, e, c, t, persist))
		if start and persist:
			self.push(e, c, t)

	def poll(self):
		"""T.poll() -> None

		Poll for the next timer event. If any trigger push
		a "Timer" event onto the queue. Reset timers
		that are marked with the forever flag.
		"""

		for timer in self.timers[:]:
			done, (e, c, t) = timer.poll()
			if done:
				self.push(e, c, t)
				if not timer.persist:
					self.timers.remove(timer)


class Timer(object):
	"""Timer(s, e, c, t, persist) -> new timer object

	Creates a new timer object which when triggered
	will return an event to be pushed onto the event
	queue held by the Timers component.
	"""

	def __init__(self, s, e, c, t, persist):
		"initializes x; see x.__class__.__doc__ for signature"

		self.s = s
		self.e = e
		self.c = c
		self.t = t
		self.persist = persist

		self.reset()

	def reset(self):
		"""T.reset() -> None

		Reset the timer.
		"""

		self._eTime = time() + self.s

	def poll(self):
		"""T.poll() -> done, (e, c, t)

		Check if this timer is ready to be triggered.
		If so, return True, (e, c, t), otherwise
		return False, (None, None, None).

		If timer is persistent, reset it after triggering.
		"""

		if time() > self._eTime:
			if self.persist:
				self.reset()
			return True, (self.e, self.c, self.t)
		else:
			return False, (None, None, None)
