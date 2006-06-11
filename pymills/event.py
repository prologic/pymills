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

Channels must be registered by calling EventManager.addChannel
There is one special channel:
   name=global, channel=0: The global channel.

An event sent to the global channel will notify _all_ filters
and listeners of that event. Filters and listeners of the
global channel will recieve events first.

Example Usage:
...
"""

import time

class EventError(Exception):
	pass

class Event:
	"""Event(**kwargs) -> new event object

	Create a new event object populating it with the given
	dictionary of keyword arguments.
	"""

	def __init__(self, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		self.__dict__.update(kwargs)
		self._time = time.time()
	
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

		self._channels = {}

		self._filters = {}
		self._listeners = {}
		self._queue = []

		self.addChannel("global")

	def _add(self, container, callable, *channels):
		# x._add(container, callable, *channels) -> None
		#
		# For every channel in channels add the given callable
		# to the container with channel as the key.

		if len(channels) == 0:
			container[0].append(callable)
		else:
			for channel in channels:
				if not type(channel) == int:
					raise EventError("type(int) expected for channel")
				try:
					container[channel].append(callable)
				except KeyError:
					raise EventError("No such channel: %d" % channel)
	
	def _remove(self, container, callable, *channels):
		# x._remove(container, callable, *channels) -> None
		#
		# Remove the given callable from the container's
		# channel. If no channels are given, _all_ callable
		# functions are removed from the container.

		if len(channels) == 0:
			keys = container.keys()
		else:
			keys = channels

		for channel in keys:
			if not type(channel) == int:
				raise EventError("type(int) expected for channel")
			try:
				container[channel].remove(callable)
			except KeyError:
				raise EventError("No such channel: %d" % channel)

	def getChannelID(self, name):
		return self._channels.get(name, None)

	def addChannel(self, name):
		channel = len(self._channels)
		self._channels[name] = channel
		self._filters[channel] = []
		self._listeners[channel] = []

	def removeChannel(self, name):
		channel = self.getChannelID(name)
		if channel is not None:
			del self._filters[channel]
			del self._listeners[channel]
			del self._channels[name]

	def addListener(self, listener, *channels):
		"""E.addListener(listener, *channels) -> None

		Add the listener to the given channels.
		If no channels are given, the listener will receive
		all events.
		"""

		if callable(listener):
			self._add(self._listeners, listener, *channels)
		else:
			raise EventError("listener must be callable")

	def addFilter(self, filter, *channels):
		"""E.addFilter(filter, *channels) -> None

		Add the filter to the given channels.
		If no channels are given, the filter will receive
		all events.
		"""

		if callable(filter):
			self._add(self._filters, filter, *channels)
		else:
			raise EventError("filter must be callable")
	
	def removeListener(self, listener, *channels):
		"""E.removeListener(listener, *channels) -> None

		Remove the listener from the given channels.
		If no channels are given, the listener will be removed
		from all channels. Also the listener will be removed
		from listening to all events.
		"""

		self._remove(self._listeners, listener, *channels)

	def removeFilter(self, filter, *channels):
		"""E.removeFilter(filter, *channels) -> None

		Remove the filter from the given channels.
		If no channels are given, the filter will be removed
		from all channels. Also the filter will be removed
		from listening to all events.
		"""

		self._remove(self._filters, filter, *channels)
	
	def push(self, event, channel, source=None):
		"Synonym of pushEvent"

		self.pushEvent(event, channel, source)

	def pushEvent(self, event, channel, source=None):
		"""E.pushEvent(event, channel, source) -> None

		Push the given event onto the channel.
		This will queue the event up to be processes later
		by flushEvents.
		"""

		if channel == 0:
			raise EventError("You cannot push events to the global channel")

		self._queue.append((event, channel, source))
	
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

		if channel == 0:
			raise EventError("You cannot send events to the global channel")

		event._source = source
		event._channel = channel
		if not hasattr(event, "_time"):
			event._time = time.time()

		filters = self._filters.get(0, []) + \
				self._filters.get(channel, [])
		listeners =	self._listeners.get(0, []) + \
				self._listeners.get(channel, [])

		for filter in filters:
			halt, newEvent = filter(event)
			if halt:
				return
			else:
				event = newEvent

		for listener in listeners:
			listener(event)

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
