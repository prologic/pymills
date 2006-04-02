# Filename: event.py
# Module:	event
# Date:		2nd April 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Event Library

....
"""

class Event:

	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)
	
	def __repr__(self):
		attrs = ((k, v) for k, v in self.__dict__.items()
				if not k.startswith("__"))
		attrStrings = ("%s=%s" % (k, v) for k, v in attrs)
		return "Event(%s)" % ", ".join(attrStrings)

	__str__ = __repr__

class EventManager:

	def __init__(self):
		self._allFilters = []
		self._filters = {}
		self._allListeners = []
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

			if len(channels) == 0:
				self._allListeners.append(listener)
			else:
				self._add(self._listeners, listener, channels)
		else:
			raise ValueError("listener must be callable")

	def addFilter(self, filter, *channels):

		if callable(filter):

			if len(channels) == 0:
				self._allFilters.append(filter)
			else:
				self._add(self._filters, filter, channels)
		else:
			raise ValueError("filter must be callable")
	
	def removeListener(self, listener, *channels):
		if listener in self._allListeners:
			self._allListeners.remove(listener)
		self._remove(self._listeners, listener, channels)

	def removeFilter(self, filter, *channels):
		if filter in self._allFilters:
			self._allFilters.remove(filter)
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
		filters = self._filters.get(channel, []) + self._allFilters
		listeners = self._listeners.get(channel, []) + self._allListeners

		for filter in filters:
			r = filter(event)
			if r is not None:
				event = r
			else:
				return

		for listener in listeners:
			listener(event)

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
