# Filename: event.py
# Module:	event
# Date:		2nd April 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Event Library

....
"""

DISCARD = 1

class Event:

	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

class EventManager:

	def __init__(self):
		self._filters = {}
		self._listeners = {}
		self._queue = []

	def _add(self, container, callable, channels):
		for channel in channels:
			if not container.has_key(channel):
				container[channel] = []
			container[channel].append(callable)
	
	def _remove(self, container, callable, channels):
		if len(channels) == 0:
			keys = container.keys()
		else:
			keys = channels

		for channel in keys:
			container[channel].remove(callable)

	def addListener(self, listener, *channels):
		if callable(listener):
			self._add(self._listeners, listener, channels)
		else:
			raise ValueError("listener must be callable")

	def addFilter(self, filter, *channels):
		if callable(filter):
			self._add(self._filters, filter, channels)
		else:
			raise ValueError("filter must be callable")
	
	def removeListener(self, listener, *channels):
		self._remove(self._listeners, listener, channels)

	def removeFilter(self, filter, *channels):
		self._remove(self._filters, filter, channels)
	
	def pushEvent(self, event, channel, source=None):

		queue = self._queue

		queue.append((event, channel, source))
	
	def flushEvents(self):

		queue = self._queue

		for event, channel, source in queue[:]:
			self.sendEvent(event, channel, source)
			queue.remove((event, channel, source))

	def sendEvent(self, event, channel, source=None):

		event.source = source
		filters = self._filters.get(channel, [])
		listeners = self._listeners.get(channel, [])

		for filter in filters:

			action = filter(event)

			if action == DISCARD:
				return

		for listener in listeners:
			listener(event)

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
