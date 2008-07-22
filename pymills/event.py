# Module:	event
# Date:		2nd April 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Event Library

Library for developing Event Driven Applications.
This library supports listeners, filters and the
queuing of events. Events are formed by constructing
a new Event object, which could be sub-classes.
Really any object could be used as the 'event'.

Channels are automatically registered by each Component
that is linked to an Manager. All methods/functions
of the component that are marked with a filter or listener
decorator are added to the appropiate channel of the
event manager given to it.

Events cannot be sent to or pushed onto the global channel.
Instead, any filters/listeners that are on this channel
will receive '''all''' events. Any filter/listener on this
channel has first priority.

WHen an event is sent to either a filter or listener's
handler, the event manager will '''try''' to apply the
event's date (args and kwargs) to that handler. The handler
of a filter or listener thus becomes an API which must be
conformed to.

If any error occurs, an EventError is raised with the
appropiate message.

A Component is an object that holds a copy of the
Manager instnace and automatically sets up any
filters/listeners found in the class. Filter/listener
methods must start with "on" and must have the
attribute "filter" or "listener" set to True. All
components are singletons, that is they can only be
instantiated once.
"""

import sys
import socket
import select
from time import sleep
import cPickle as pickle
from threading import Thread
from pickle import PickleError
from inspect import getmembers, ismethod, getargspec

from utils import caller

POLL_INTERVAL=0.001

class EventError(Exception):
	"Event Error"

class UnhandledEvent(EventError):
	"Unhandled Event Error"

	def __init__(self, event, channel):
		super(UnhandledEvent, self).__init__(event, channel)

class FilterEvent(Exception):
	"Filter Event Exception"

def filter(channel="global"):
	"Decorator function for a filter"

	def decorate(f):
		f.filter = True
		f.channel = channel
		f.args = getargspec(f)[0]
		if len(f.args) > 0:
			if f.args[0] == "self":
				del f.args[0]
		return f
	return decorate

def listener(channel="global"):
	"Decorator function for a listener"

	def decorate(f):
		f.listener = True
		f.channel = channel
		f.args = getargspec(f)[0]
		if len(f.args) > 0:
			if f.args[0] == "self":
				del f.args[0]
		return f
	return decorate

def send(handlers, event, channel, target=None):
	"""send(handlers event, channel, target=None) -> None

	Given a list of handlers of the given channel (plus the
	global channel), send the given event. if target is given
	send this send this event to the given target component.

	Filters are processed first.
	Filters must return a tuple (halt, event)
	A filter may:
	 * Return a new event
	 * Return the same event in tact
	If halt is True, the event is discarded and no
	further filters or listeners can recieve this event.
	"""

	if channel == "global":
		raise EventError("Events cannot be sent to the global channel")

	event._channel = channel
	event._target = target

	if not handlers:
		raise UnhandledEvent(event, channel)

	for handler in handlers:
		try:
			args = handler.args
			if args:
				if args[0] in ("event", "evt", "e",):
					handler(event, *event.args, **event.kwargs)
				else:
					handler(*event.args, **event.kwargs)
			else:
				handler()
		except FilterEvent:
			return

def _sortHandlers(x, y):
	if hasattr(x, "filter") and hasattr(y, "filter"):
		return 0
	elif hasattr(x, "filter"):
		return -1
	else:
		return 1

class Manager(object):
	"""Manager() -> new event manager

	Create a new event manager which manages events.
	If server=True, this will listen on the default port
	of 64000 allowing events to be to other connected
	remote event managers.
	"""

	def __init__(self, *args, **kwargs):
		super(Manager, self).__init__()

		self._handlers = set()
		self._channels = {"global": []}
		self._queue = []
		self.manager = self

	def __len__(self):
		return len(self._queue)

	def getChannels(self):
		"""E.getChannels() -> list

		Return a list of all available channels.
		"""

		return self._channels.keys()

	def getHandlers(self, channel=None):
		"""E.getHandlers(channel=None) -> list

		Givan a channel return all handlers on that channel.
		If channel is None, then return all handlers.
		"""

		if channel:
			return self._channels.get(channel, [])
		else:
			return self._handlers

	def add(self, handler, *channels):
		"""E.add(handler, *channels) -> None

		Add a new filter or listener to the event manager
		adding it to all channels specified. if no channels
		are given, add it to the global channel.
		"""

		if len(channels) == 0:
			channels = ["global"]

		if not hasattr(handler, "filter") and \
				not hasattr(handler, "listener"):
			raise EventError(
					"%s is not a filter or listener" % handler)

		self._handlers.add(handler)

		for channel in channels:
			if self._channels.has_key(channel):
				if handler not in self._channels[channel]:
					self._channels[channel].append(handler)
					self._channels[channel].sort(
							cmp=_sortHandlers)
			else:
				self._channels[channel] = [handler]

	def remove(self, handler, *channels):
		"""E.remove(handler, *channels) -> None

		Remove the given filter or listener from the
		event manager removing it from all channels
		specified. If no channels are given, '''all'''
		instnaces are removed. This will succeed even
		if the specified handler has already been
		removed.
		"""

		if len(channels) == 0:
			keys = self._channels.keys()
		else:
			keys = channels

		if handler in self._handlers:
			self._handlers.remove(handler)

		for channel in keys:
			if handler in self._channels[channel]:
				self._channels[channel].remove(handler)

	def push(self, event, channel, target=None):
		"""E.push(event, channel, target=None) -> None

		Push the given event onto the given channel.
		This will queue the event up to be processed later
		by flushEvents. If target is given, the event will
		be queued for processing by the component given by
		target.
		"""

		if self.manager == self:
			self._queue.append((event, channel, target))
		else:
			self.manager.push(event, channel, target)

	def flush(self):
		"""E.flushEvents() -> None

		Flush all events waiting in the queue.
		Any event waiting in the queue will be sent out
		to filters/listeners.
		"""

		if self.manager == self:
			for event in self._queue[:]:
				try:
					self.send(*event)
				finally:
					self._queue.remove(event)
		else:
			self.manager.flush()

	def send(self, event, channel, target=None):
		"""E.send(event, channel, target=None) -> None

		Send the given event to filters/listeners on the
		channel specified. If target is given, send this
		event to filters/listeners of the given target
		component.
		"""

		if self.manager == self:
			if target:
				channel = "%s:%s" % (target, channel)
			handlers = self.getHandlers("global") + self.getHandlers(channel)
			send(handlers, event, channel, target)
		else:
			self.manager.send(event, channel, target)

class Component(Manager):
	"""Component(Manager) -> new component object

	This should be sub-classed with methods defined for filters
	and listeners. Only one instance of any component can be
	instantiated. Further instantiation of the same component
	results in the same instance previously instantiated.

	Any filter/listeners found in the class will automatically
	be setup and added to the event manager. If a channel is
	requireed one will be added.

	Filters and Listeners are defined like so:

	C{
	@filter()
	def onFOO(self, event):
		return True, event
	
	@listener()
	def onBAR(self, event):
		print event
	}
	"""

	def __init__(self, *args, **kwargs):
		super(Component, self).__init__(*args, **kwargs)

		manager = kwargs.get("manager", None)

		if manager is not None:
			self.manager = manager
		else:
			self.manager = self
			if len(args) > 0:
				if isinstance(args[0], Component) or isinstance(args[0], Manager):
					self.manager = args[0]

		self._links = []

		self.channel = kwargs.get(
				"channel",
				getattr(self.__class__, "channel", None))

		self.register(self.manager)

	def __del__(self):
		self.unregister()

	def register(self, manager):
		handlers = [x[1] for x in getmembers(
			self, lambda x: ismethod(x) and
			callable(x) and x.__name__.startswith("on") and
			(hasattr(x, "filter") or hasattr(x, "listener")))]

		for handler in handlers:
			if self.channel:
				channel = "%s:%s" % (self.channel, handler.channel)
			else:
				channel = handler.channel

			manager.add(handler, channel)

			self._handlers.add(handler)

			if self._channels.has_key(channel):
				self._channels[channel].append(handler)
				self._channels[channel].sort(
						cmp=lambda x, y: hasattr(x, "filter"))
			else:
				self._channels[channel] = [handler]

	def unregister(self):
		"""C.unregister() -> None

		Unregister all listeners/filters associated with
		this component
		"""

		for handler in self.getHandlers().copy():
			self.manager.remove(handler)
			self.remove(handler)

	def link(self, component):
		"""C.link(component) -> None

		Link the given component to the current component.
		"""

		if component not in self._links:
			self._links.append(component)
			component.register(self)

	def unlink(self, component):
		"""C.unlink(component) -> None

		Un-Link the given component from the current component.
		"""

		if component in self._links:
			self._links.remove(component)
			component.unregister(self)

class Worker(Component, Thread):

	def __init__(self, *args, **kwargs):
		super(Worker, self).__init__(*args, **kwargs)

		autoStart = kwargs.get("autoStart", False)
		if autoStart:
			self.start()

	def start(self):
		self.__running = True
		self.setDaemon(True)
		super(Worker, self).start()

	def stop(self):
		self.__running = False

	def isRunning(self):
		return self.__running

	def run(self):
		while self.isRunning():
			sleep(1)

class Event(object):
	"""Event(*args, **kwargs) -> new event object

	Create a new event object populating it with the given
	list of arguments and dictionary of keyword arguments.
	"""

	def __init__(self, *args, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		super(Event, self).__init__(*args, **kwargs)

		self.args = args
		self.kwargs = kwargs
		self.__dict__.update(kwargs)

	def __repr__(self):
		"x.__repr__() <==> repr(x)"

		attrs = ((k, v) for k, v in self.kwargs.items())
		attrStrings = ("%s=%s" % (k, v) for k, v in attrs)
		channel = getattr(self, "_channel", "None")
		return "<%s/%s %s {%s}>" % (
				self.__class__.__name__,
				channel,
				self.args, ", ".join(attrStrings))

	def __getitem__(self, x):
		"x.__getitem__(y) <==> x[y]"

		if type(x) == int:
			return self.args[x]
		elif type(x) == str:
			return self.kwargs[x]
		else:
			raise KeyError(x)

###
### FIXME: Refactor RemoteManager to sub-class pymills.net.sockets.TCPServer
###

class Remote(object):
	pass
