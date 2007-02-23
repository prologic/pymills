# Filename: event.py
# Module:	event
# Date:		2nd April 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Event Library

Library for developing Event Driven Applications. This library
supports listeners, filters and the queuing of events.
Events are formed by constructing a new Event object, which
could be sub-classes. Really any object could be used as
the 'event'.

Channels must be registered by calling EventManager.addChannel
There is one special channel:
   name=global, channel=0: The global channel.

Events cannot be sent to or pushed onto the global channel.
Instead, any filters/listeners that are on this channel
will receive '''all''' events. Any filter/listener on this
channel has first priority.

WHen an event is sent to either a filter or listener's
callable, the event manager will '''try''' to apply the
event's date (args and kwargs) to that callable. The callable
of a filter or listener thus becomes an API which must be
conformed to.

If any error occurs, an EventError is raised with the
appropiate message.

A Component is an object that holds a copy of the EventManager
instnace and automatically sets up any filters/listeners
found in the class. Filter/listener methods must start with
"on" and must have the attribute "filter" or "listener"
set to True. All components are singletons, that is they can
only be instantiated once.
"""

import time
import socket
import inspect

class EventError(Exception):
	"Event Error Exception"

def filter(*args):
	"Decorator function for a filter"

	def decorate(f):
		f.filter = True
		if len(args) == 1:
			setattr(f, "channel", args[0])
		else:
			setattr(f, "channel", "global")
		return f
	return decorate

def listener(*args):
	"Decorator function for a listener"

	def decorate(f):
		f.listener = True
		if len(args) == 1:
			setattr(f, "channel", args[0])
		else:
			setattr(f, "channel", "global")
		return f
	return decorate

class Component(object):
	"""Component(event) -> new component object

	This should be sub-classed with methods defined for filters
	and listeners. Only one instance of any component can be
	instantiated. Further instantiation of the same component
	results in the same instance previously instantiated.

	Any filter/listeners found in the class will automatically
	be setup and added to the event manager. If a channel is
	requireed one will be added.

	Filters and Listeners are defined like so:

	{{{
	#!python

	@filter()
	def onFOO(self, event):
		return True, event

	@listener()
	def onBAR(self, event):
		print event
	}}}
	"""

	instances = {}

	def __new__(cls, event, *args, **kwargs):
		"Creates x; see x.__class__.__doc__ for signature"

		if cls in cls.instances:
			return cls.instances[cls]
		
		self = super(cls.__class__, cls).__new__(cls, *args,
				**kwargs)

		self.event = event

		events = [(x[0], x[1]) for x in inspect.getmembers(
			self, lambda x: inspect.ismethod(x) and
			callable(x) and
			(hasattr(x, "filter") or hasattr(x, "listener")))]

		for event, handler in events:
			if not hasattr(handler, "channel"):
				handler.channel = event
			channel = self.event.getChannelID(handler.channel)
			if channel is None:
				channel = self.event.addChannel(handler.channel)
			self.event.add(handler, channel)

		self.instances[cls] = self
		return self

	def unregister(self):
		"""C.unregister() -> None

		Unregister all listeners/filters associated with
		this component
		"""

		events = [(x[0], x[1]) for x in inspect.getmembers(
			self, lambda x: inspect.ismethod(x) and
			callable(x) and
			(hasattr(x, "filter") or hasattr(x, "listener")))]

		for event, handler in events:
			if not hasattr(handler, "channel"):
				handler.channel = event
			channel = self.event.getChannelID(handler.channel)
			if channel is None:
				channel = self.event.addChannel(handler.channel)
			self.event.remove(handler, channel)

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
	
	def __getitem__(self, x):
		if type(x) == int:
			return self._args[x]
		elif type(s) == str:
			return self._kwargs[x]
		else:
			raise TypeError(
					"x: expected int or str type, got %s" % type(x))
	
	def __repr__(self):
		"x.__repr__() <==> repr(x)"

		attrs = ((k, v) for k, v in self.__dict__.items()
				if not k.startswith("_"))
		attrStrings = ("%s=%s" % (k, v) for k, v in attrs)
		return "<%s %s {%s}>" % (
				self.__class__.__name__,	self._args, ", ".join(attrStrings))

	__str__ = __repr__

class EventManager:
	"""EventManager() -> new event manager

	Create a new event manager which manages events.
	If server=True, this will listen on the default port
	of 64000 allowing events to be to other connected
	remote event managers.
	"""

	def __init__(self, server=False, port=64000):
		"initializes x; see x.__class__.__doc__ for signature"

		if server:
			pass

		self._channels = {
				"global": 0}

		self._filters = {0: []}
		self._listeners = {0: []}
		self._queue = []

	def add(self, callable, *channels):
		"""E.add(callable, *channels) -> None

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
						"Channel %s not found" % channel)
	
	def remove(self, callable, *channels):
		"""E.remove(callable, *channels) -> None
		
		Remove the given filter or listener from the
		event manager removing it from all channels
		specified. If no channels are given, '''all'''
		instnaces are removed. This will succeed even
		if the specified callable has already been
		removed.
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
				try:
					container[channel].remove(callable)
				except ValueError:
					pass
			except KeyError:
				raise EventError(
						"Channel %d not found" % channel)

	def getChannelID(self, name):
		"Return the channel id given by name"

		return self._channels.get(name, None)

	def addChannel(self, name):
		"Add a new channel with the name given"

		channel = len(self._channels)
		self._channels[name] = channel
		self._filters[channel] = []
		self._listeners[channel] = []
		return channel

	def removeChannel(self, name):
		"""Remove a channel given by name

		This also clears the filters and listeners containers
		of that channel, any filters/listeners in that channel
		are removed.
		"""

		channel = self.getChannelID(name)
		if channel is not None:
			del self._filters[channel]
			del self._listeners[channel]
			del self._channels[name]

	def push(self, event, channel, source=None):
		"Synonym of pushEvent"

		self.pushEvent(event, channel, source)

	def pushEvent(self, event, channel, source=None):
		"""E.pushEvent(event, channel, source=None) -> None

		Push the given event onto the given channel.
		This will queue the event up to be processes later
		by flushEvents. If a channel is given as a str
		the appropiate channel id will be retrieved.
		Events cannot be pushed onto the global channel,
		doing so will raise an error.
		"""

		if type(channel) == str:
			channel = self.getChannelID(channel)

		if channel == self.getChannelID("global"):
			raise EventError(
					"You cannot push events onto the global channel")

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
			try:
				self.sendEvent(event, channel, source)
			finally:
				queue.remove((event, channel, source))

	def send(self, event, channel, source=None):
		"Synonym of sendEvent"

		return self.sendEvent(event, channel, source)
	
	def sendEvent(self, event, channel, source=None):
		"""E.sendEvent(event, channel, source=None) -> None

		Send the given event to listeners on the given channel.
		THe _source and _time of the event are populated in
		the event object.

		Filters are processed first.
		Filters must return a tuple (halt, event)
		A filter may:
		 * Return a new event
		 * Return the same event in tact
		If halt is True, the event is discarded and no
		further filters or listeners can recieve this event.
		"""

		def call(callable, event):
			args, vargs, kwargs, default = inspect.getargspec(
					callable)

			if len(args) > 0 and args[0] == "self":
				args.remove("self")

			try:
				if len(args) > 0 and args[0] == "event":
					if len(args) == 1:
						if kwargs is None:
							return callable(event)
						else:
							return callable(event, **event._kwargs)
					else:
						return callable(event, *event._args,
								**event._kwargs)
				else:
					return callable(*event._args,
							**event._kwargs)
			except Exception, e:
				raise
				raise EventError(
						"API Error with filter/listener '%s': %s" % (
							callable, e))

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
			try:
				halt, newEvent = call(filter, event)
			except TypeError:
				raise
				raise EventError(
						"Filter '%s' did not return (halt, event)" %
						filter)
			if halt:
				return
			else:
				event = newEvent

		for listener in listeners:
			r = call(listener, event)
			if r is not None:
				return r
