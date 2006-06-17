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

An event sent to the global channel will notify '''all'''
filters and listeners of that event. Filters and listeners
of the global channel will recieve events first.

WHen an event is sent to either a filter or listener's
callable, the event manager will '''try''' to apply the
event's date (args and kwargs) to that function. Tke callable
of a filter or listener thus becomes an API which must be
conformed to.

Example Usage:
...
"""

import time
import inspect

class EventError(Exception):
	pass

class Component(object):

	instances = {}

	def __new__(cls, event):
		if cls in Component.instances:
			return Component.instances[cls]
		
		self = super(
				Component, cls).__new__(cls)
		Component.instances[cls] = self

		self.event = event

		events = [(x[0][2:], x[1]) for x in inspect.getmembers(
			self, lambda x: inspect.ismethod(x) and
			callable(x) and x.__name__.startswith("on") and
			(hasattr(x, "filter") or hasattr(x, "listener")))]

		for event, handler in events:
			channel = self.event.getChannelID(event)
			if channel is None:
				channel = self.event.addChannel(event)
			self.event.add(handler, channel)

		return self

class Event:
	"""Event(*args, **kwargs) -> new event object

	Create a new event object populating it with the given
	list of arguments and dictionary of keyword arguments.
	"""

	def __init__(self, *args, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		self._args = args
		self._kwargs = kwargs
		self._time = time.time()
		self.__dict__.update(kwargs)
	
	def __repr__(self):
		"x.__repr__() <==> repr(x)"

		attrs = ((k, v) for k, v in self.__dict__.items()
				if not k.startswith("_"))
		attrStrings = ("%s=%s" % (k, v) for k, v in attrs)
		return "<Event (%s) {%s}>" % (
				self._args, ", ".join(attrStrings))

	__str__ = __repr__

class EventManager:
	"""EventManager() -> new event manager

	Create a new event manager which manages events.
	"""

	def __init__(self):
		"initializes x; see x.__class__.__doc__ for signature"

		self._channels = {
				0: "global"}

		self._filters = {}
		self._listeners = {}
		self._queue = []

	def add(self, callable, *channels):
		"""E._add(callable, *channels) -> None

		Add a new filter or listener to the event manager
		adding it to all channels specified. if no channels
		are given, add it to the global channel.
		"""

		if len(channels) == 0:
			channels = [0]

		for channel in channels:

			if type(channel) == str:
				channel = self.getChannelID(channel)

			if hasattr(callable, "filter"):
				container = self._filters
			elif hasattr(callable, "listener"):
				container = self._listeners
			else:
				raise EventError("Given callable '%s' is" \
						"not a filter or listener" % callable)

			try:
				container[channel].append(callable)
			except KeyError:
				raise EventError(
						"Channel %d not found" % channel)
	
	def remove(self, callable, *channels):
		"""E._remove(callable, *channels) -> None
		
		Remove the given filter or listener from the
		event manager removing it from all channels
		specified. If no channels are given, '''all'''
		instnaces are removed.
		"""

		if len(channels) == 0:
			keys = self._channels.keys()
		else:
			keys = channels

		for channel in keys:

			if type(channel) == str:
				channel = self.getChannelID(channel)

			if hasattr(callable, "filter"):
				container = self._filters
			elif hasattr(callable, "listener"):
				container = self._listeners
			else:
				raise EventError("Given callable '%s' is" \
						"not a filter or listener" % callable)

			try:
				container[channel].remove(callable)
			except KeyError:
				raise EventError(
						"Channel %d not found" % channel)

	def getChannelID(self, name):
		return self._channels.get(name, None)

	def addChannel(self, name):
		channel = len(self._channels)
		self._channels[name] = channel
		self._filters[channel] = []
		self._listeners[channel] = []
		return channel

	def removeChannel(self, name):
		channel = self.getChannelID(name)
		if channel is not None:
			del self._filters[channel]
			del self._listeners[channel]
			del self._channels[name]

	def push(self, channel, source=None, event=Event()):
		"Synonym of pushEvent"

		self.pushEvent(channel, source, event)

	def pushEvent(self, channel, source=None, event=Event()):
		"""E.pushEvent(event, channel, source) -> None

		Push the given event onto the channel.
		This will queue the event up to be processes later
		by flushEvents.
		"""

		if type(channel) == str:
			channel = self.getChannelID(channel)

		if channel == 0:
			raise EventError(
					"You cannot push events to the global channel")

		self._queue.append((channel, source, event))
	
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

		for channel, source, event in queue[:]:
			self.sendEvent(channel, source, event)
			queue.remove((channel, source, event))

	def send(self, channel, source=None, event=Event()):
		"Synonym of sendEvent"

		self.sendEvent(channel, source, event)
	
	def sendEvent(self, channel, source=None, event=Event()):
		"""E.sendEvent(channel, source, event=Event()) -> None

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

		def call(callable, event):
			args, vargs, kwargs, default = inspect.getargspec(
					callable)

			if len(args) > 0 and args[0] == "self":
				args.remove("self")

			if len(args) > 0 and args[0] == "event":
				return callable(event, *event._args, **event._kwargs)
			return callable(*event._args, **event._kwargs)

		if type(channel) == str:
			channel = self.getChannelID(channel)

		if channel == 0:
			raise EventError(
					"You cannot send events to the global channel")

		if source is not None:
			event._source = source
		else:
			event._source = self
		event._channel = channel
		if not hasattr(event, "_time"):
			event._time = time.time()

		filters = self._filters.get(0, []) + \
				self._filters.get(channel, [])
		listeners =	self._listeners.get(0, []) + \
				self._listeners.get(channel, [])

		for filter in filters:
			halt, newEvent = call(filter, event)
			if halt:
				return
			else:
				event = newEvent

		for listener in listeners:
			call(listener, event)

def test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	test()
