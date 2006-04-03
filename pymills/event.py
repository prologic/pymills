# Filename: event.py
# Module:	event
# Date:		2nd April 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Event Library

Library for developing Event Driven Applications. This library
supports listeners, filters and the queuing of events.
Events are formed by constructing a new Event object, which
could be sub-classes. Really any object could be used as
the 'event'.

Example Usage:
...
"""

import time

class Event:
	"""Event(**kwargs) -> new event object

	Create a new event object populating it with the given
	dictionary of keyword arguments.
	"""

	def __init__(self, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		self.__dict__.update(kwargs)
	
	def __repr__(self):
		"x.__repr__() <==> repr(x)"

		attrs = ((k, v) for k, v in self.__dict__.items()
				if not k.startswith("__"))
		attrStrings = ("%s=%s" % (k, v) for k, v in attrs)
		return "Event(%s)" % ", ".join(attrStrings)

	__str__ = __repr__

class EventManager:
	"""EventManager() -> new event manager

	Create a new event manager which manages events.
	"""

	def __init__(self):
		"initializes x; see x.__class__.__doc__ for signature"

		self._allFilters = []
		self._filters = {}
		self._allListeners = []
		self._listeners = {}
		self._queue = []

	def _add(self, container, callable, channels):
		# x._add(container, callable, channels) -> None
		#
		# For every channel in channels add the given callable
		# to the container with channel as the key.

		for channel in channels:
			if not container.has_key(channel):
				container[channel] = []
			container[channel].append(callable)
	
	def _remove(self, container, callable, channels):
		# x._remove(container, callable, channels) -> None
		#
		# Remove the given callable from the container's
		# channel. If no channels are given, _all_ callable
		# functions are removed from the container.

		if len(channels) == 0:
			keys = container.keys()
		else:
			keys = channels

		for channel in keys:
			container[channel].remove(callable)

	def addListener(self, listener, *channels):
		"""E.addListener(listener, *channels) -> None

		Add the listener to the given channels.
		If no channels are given, the listener will receive
		all events.
		"""

		if callable(listener):

			if len(channels) == 0:
				self._allListeners.append(listener)
			else:
				self._add(self._listeners, listener, channels)
		else:
			raise ValueError("listener must be callable")

	def addFilter(self, filter, *channels):
		"""E.addFilter(filter, *channels) -> None

		Add the filter to the given channels.
		If no channels are given, the filter will receive
		all events.
		"""

		if callable(filter):

			if len(channels) == 0:
				self._allFilters.append(filter)
			else:
				self._add(self._filters, filter, channels)
		else:
			raise ValueError("filter must be callable")
	
	def removeListener(self, listener, *channels):
		"""E.removeListener(listener, *channels) -> None

		Remove the listener from the given channels.
		If no channels are given, the listener will be removed
		from all channels. Also the listener will be removed
		from listening to all events.
		"""

		if listener in self._allListeners:
			self._allListeners.remove(listener)
		self._remove(self._listeners, listener, channels)

	def removeFilter(self, filter, *channels):
		"""E.removeFilter(filter, *channels) -> None

		Remove the filter from the given channels.
		If no channels are given, the filter will be removed
		from all channels. Also the filter will be removed
		from listening to all events.
		"""
		if filter in self._allFilters:
			self._allFilters.remove(filter)
		self._remove(self._filters, filter, channels)
	
	def push(self, event, channel, source=None):
		"Synonym of pushEvent"

		self.pushEvent(event, channel, source)

	def pushEvent(self, event, channel, source=None):
		"""E.pushEvent(event, channel, source) -> None

		Push the given event onto the channel.
		This will queue the event up to be processes later
		by flushEvents.
		"""

		event._time = time.time()
		queue = self._queue
		queue.append((event, channel, source))
	
	def flush(self):
		"Synonym of flushEvents"

		self.flushEvents()
	
	def flushEvents(self):
		"""E.flushEvents() -> None

		Flush all events waiting in the queue.
		Any event waiting in the queue will be sent out
		to filters/listeners.
		"""

		queue = self._queue

		for event, channel, source in queue[:]:
			self.sendEvent(event, channel, source)
			queue.remove((event, channel, source))

	def send(self, event, channel, source=None):
		"Synonym of sendEvent"

		self.sendEvent(event, channel, source)
	
	def sendEvent(self, event, channel, source=None):
		"""E.sendEvent(event, channel, source) -> None

		Send the given event to listeners on the channel.
		THe _source and _time of the event are populated in
		the event object.

		Filters are processed first. Any filter can either:
		 * return the event
		 * modify the event
		 * return a new event
		 * return None
		If a filter returns None, the event is discarded and
		no further processing of this event will occur.
		"""

		event._source = source
		if not hasattr(event, "_time"):
			event._time = time.time()

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
