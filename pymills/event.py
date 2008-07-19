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

def send(handlers, event, channel, source=None):
	"""send(handlers event, channel, source=None) -> None

	Given a list of handlers of the given channel (plus the
	global channel), send the given event.
	source is expected to be an object.

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

	event._source = source
	event._channel = channel

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

	def push(self, event, channel, source=None):
		"""E.push(event, channel, source=None) -> None

		Push the given event onto the given channel.
		This will queue the event up to be processed later
		by flushEvents. source is expected to be an object.
		"""

		if self.manager == self:
			self._queue.append((event, channel, source))
		else:
			self.manager.push(event, channel, source)

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

	def send(self, event, channel, source=None):
		"""E.send(event, channel, source=None) -> None

		Send the given event to filters/listeners on the
		channel specified.
		"""

		if hasattr(source, "channel"):
			channel = "%s:%s" % (source.channel, channel)

		if self.manager == self:
			handlers = self.getHandlers("global") + \
					self.getHandlers(channel)
	
			send(handlers, event, channel, source)
		else:
			self.manager.send(event, channel, source)

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

		if kwargs.has_key("channel"):
			self.channel = kwargs["channel"]

		self.register(self.manager)

	def __del__(self):
		self.unregister()

	def register(self, manager):
		handlers = [x[1] for x in getmembers(
			self, lambda x: ismethod(x) and
			callable(x) and x.__name__.startswith("on") and
			(hasattr(x, "filter") or hasattr(x, "listener")))]

		for handler in handlers:
			if hasattr(self, "channel"):
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

class Remote(Manager):

	def __init__(self, *args, **kwargs):
		super(Remote, self).__init__(*args, **kwargs)

		nodes = kwargs.get("nodes", ())
		if len(nodes) == 0:
			if len(args) > 0:
				if type(args[0]) in [list, tuple]:
					nodes = args[0]

		address = kwargs.get("address", "0.0.0.0")
		port = kwargs.get("port", 64000)

		self._nodes = []
		for node in nodes:
			if ":" in node:
				x = node.split(":")
				self._nodes.append((x[0], int(x[1]),))
			else:
				self._nodes.append((node, port,))

		self._address = address
		self._port = port
		self._buffer = ""

		self._ssock = socket.socket(
				socket.AF_INET,
				socket.SOCK_DGRAM)
		self._ssock.setsockopt(
				socket.SOL_SOCKET,
				socket.SO_REUSEADDR,
				1)
		self._ssock.setblocking(False)
		self._ssock.bind((address, port))

		self._csock = socket.socket(
				socket.AF_INET,
				socket.SOCK_DGRAM)
		self._csock.setsockopt(
				socket.SOL_SOCKET,
				socket.SO_REUSEADDR,
				1)
		self._csock.setsockopt(
				socket.SOL_SOCKET,
				socket.SO_BROADCAST,
				1)
		self._csock.setblocking(False)

	def __del__(self):
		self.__close__()

	def __poll__(self, wait=POLL_INTERVAL):
		try:
			r, w, e = select.select([self._ssock], [], [], wait)
			return not r == []
		except socket.error, error:
			self.__close__()
			return False

	def __read__(self, bufsize=8192):
		try:
			data, addr = self._ssock.recvfrom(bufsize)
		except socket.error, e:
			self.__close__()

		event, channel, source = pickle.loads(data)

		source = addr[0], source[1]

		if source not in self._nodes:
			self._nodes.append(source)

		try:
			super(Remote, self).send(event, channel, source)
		except UnhandledEvent:
			pass

	def __close__(self):
		self._ssock.shutdown(2)
		self._ssock.close()
		self._csock.shutdown(2)
		self._csock.close()

	def __write__(self, data):
		for node in self._nodes:
			bytes = self._csock.sendto(data, node)
			if bytes < len(data):
				raise EventError(
						"Couldn't send event to %s" % str(node))

	def process(self):
		if self.__poll__():
			self.__read__()

	def flush(self):
		if self.manager == self:
			for event, channel, source in self._queue[:]:
				try:
					try:
						super(Remote, self).send(event, channel, source)
					except UnhandledEvent:
						pass
				finally:
					self._queue.remove((event, channel, source))

				if len(self._nodes) > 0:
					if source is None:
						source = (socket.gethostname(), self._port,)
					else:
						if not type(source) == str:
							source = repr(source)

					if not type(event._source) == str:
						event._source = repr(source)

					s = pickle.dumps((event, channel, source))

					if len(self._buffer) + len(s) > 8192:
						self.__write__(self._buffer)
						self._buffer = ""
					self._buffer += s

			if not self._buffer == "":
				self.__write__(self._buffer)
				self._buffer = ""
		else:
			self.manager.flush()

	def send(self, event, channel, source=None):
		try:
			r = super(Remote, self).send(event, channel, source)
		except UnhandledEvent:
			r = None
		if not caller() == "flush":
			if source is None:
				source = (socket.gethostname(), self._port,)
			self.__write__(pickle.dumps((event, channel, source)))
		return r
