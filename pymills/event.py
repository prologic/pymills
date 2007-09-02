# Module:	event
# Date:		2nd April 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

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
import copy
import socket
import select
from time import sleep
import cPickle as pickle
from threading import Thread
from inspect import getmembers, ismethod

from utils import caller

class EventError(Exception):
	"Event Error"

class UnhandledEvent(EventError):
	"Unhandled Event Error"

	def __init__(self, event, channel):
		EventError.__init__(self, event, channel)

class FilterEvent(Exception):
	"Filter Event Exception"

def filter(channel="global"):
	"Decorator function for a filter"

	def decorate(f):
		f.filter = True
		f.channel = channel
		return f
	return decorate

def listener(channel="global"):
	"Decorator function for a listener"

	def decorate(f):
		f.listener = True
		f.channel = channel
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

	if hasattr(source, "__channelPrefix__"):
		channel = "%s:%s" % (source.__channelPrefix__, channel)

	if channel == "global":
		raise EventError("Events cannot be sent to the global channel")

	event._source = source
	event._channel = channel

	if handlers == []:
		raise UnhandledEvent(event, channel)

	r = []
	for handler in handlers:
		try:
			r.append(handler(*event._args, **event._kwargs))
		except FilterEvent:
			return
	return tuple(r)

class Manager(object):
	"""Manager() -> new event manager

	Create a new event manager which manages events.
	If server=True, this will listen on the default port
	of 64000 allowing events to be to other connected
	remote event managers.
	"""

	def __new__(cls, *args, **kwargs):
		"Creates x; see x.__class__.__doc__ for signature"

		objList = [sup.__new__(cls, *args, **kwargs)
				for sup in Manager.__bases__]
		for obj in objList[1:]:
			objList[0].__dict__.update(copy.deepcopy(obj.__dict__))

		self = objList[0]

		self._handlers = {"global": []}
		self._queue = []

		return self

	def __init__(self, log=None, debug=False):
		self._log = log
		self._debug = debug

	def __len__(self):
		return len(self._queue)

	def getHandlers(self, channel=None):
		"""E.getHandlers(channel=None) -> list

		Givan a channel return all handlers on that channel.
		If channel is None, then return all handlers.
		"""

		if channel is not None:
			return self._handlers.get(channel, [])
		else:
			handlers = []
			for x in self._handlers.values():
				handlers += x
			return handlers

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

		for channel in channels:
			if self._handlers.has_key(channel):
				self._handlers[channel].append(handler)
				self._handlers[channel].sort(
						cmp=lambda x, y: hasattr(x, "filter"))
			else:
				self._handlers[channel] = [handler]

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
			keys = self._handlers.keys()
		else:
			keys = channels

		for channel in keys:
			if handler in self._handlers[channel]:
				self._handlers[channel].remove(handler)

	def push(self, event, channel, source=None):
		"""E.push(event, channel, source=None) -> None

		Push the given event onto the given channel.
		This will queue the event up to be processed later
		by flushEvents. source is expected to be an object.
		"""

		self._queue.append((event, channel, source))

	def flush(self):
		"""E.flushEvents() -> None

		Flush all events waiting in the queue.
		Any event waiting in the queue will be sent out
		to filters/listeners.
		"""

		for event, channel, source in self._queue[:]:
			try:
				self.send(event, channel, source)
			finally:
				self._queue.remove((event, channel, source))

	def send(self, event, channel, source=None):
		"""E.send(event, channel, source=None) -> None

		Send the given event to filters/listeners on the
		channel specified.
		"""

		#TODO: Fix this

		"""
  File "/home/prologic/lib/python/pymills/event.py", line 547, in flush
    s = pickle.dumps((event, channel, source))
  File "/usr/lib/python2.5/copy_reg.py", line 76, in _reduce_ex
    raise TypeError("a class that defines __slots__ without "
TypeError: a class that defines __slots__ without defining __getstate__ cannot be pickled
		"""

#		if source is None:
#			source = self

		handlers = self.getHandlers("global") + \
				self.getHandlers(channel)

		if self._debug:
			if self._log is not None:
				self._log.debug(event)
			else:
				print >> sys.stderr, event

		return send(handlers, event, channel, source)

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

	def __new__(cls, *args, **kwargs):
		"Creates x; see x.__class__.__doc__ for signature"

		if cls in cls.instances:
			return cls.instances[cls]

		if len(args) > 0 and isinstance(args[0], Manager):
			event = args[0]
			args = args[1:]
		else:
			event = None

		objList = [sup.__new__(cls, *args, **kwargs)
				for sup in Component.__bases__]
		for obj in objList[1:]:
			objList[0].__dict__.update(copy.deepcopy(obj.__dict__))

		self = objList[0]

		if event is None:
			self.event = self
		else:
			self.event = event

		if self.event is not self:
			handlers = [x[1] for x in getmembers(
				self, lambda x: ismethod(x) and
				callable(x) and x.__name__.startswith("on") and
				(hasattr(x, "filter") or hasattr(x, "listener")))]

			for handler in handlers:
				if hasattr(self, "__channelPrefix__"):
					channel = "%s:%s" % (
							self.__channelPrefix__,
							handler.channel)
				else:
					channel = handler.channel

				self.event.add(handler, channel)

				if self._handlers.has_key(channel):
					self._handlers[channel].append(handler)
					self._handlers[channel].sort(
							cmp=lambda x, y: hasattr(x, "filter"))
				else:
					self._handlers[channel] = [handler]

		self.instances[cls] = self
		return self

	def __del__(self):
		self.unregister()

	def link(self, component):
		"""C.link(component) -> None

		Link the given component to the current component.
		"""

		handlers = [x[1] for x in getmembers(
			component, lambda x: ismethod(x) and
			callable(x) and x.__name__.startswith("on") and
			(hasattr(x, "filter") or hasattr(x, "listener")))]

		for handler in handlers:
			if hasattr(component, "__channelPrefix__"):
				channel = "%s:%s" % (
						component.__channelPrefix__,
						handler.channel)
			else:
				channel = handler.channel

			self.add(handler, channel)

	def unregister(self):
		"""C.unregister() -> None

		Unregister all listeners/filters associated with
		this component
		"""

		for handler in self.getHandlers():
			self.event.remove(handler)
			self.remove(handler)

class Worker(Component, Thread):

	def __init__(self, *args):
		Component.__init__(self)
		Thread.__init__(self)

		self.__running = True
		self.setDaemon(True)
		self.start()

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

		self._args = args
		self._kwargs = kwargs
		self.__dict__.update(kwargs)

	def __repr__(self):
		"x.__repr__() <==> repr(x)"

		attrs = ((k, v) for k, v in self.__dict__.items()
				if not k.startswith("_"))
		attrStrings = ("%s=%s" % (k, v) for k, v in attrs)
		channel = getattr(self, "_channel", "None")
		return "<%s/%s %s {%s}>" % (
				self.__class__.__name__,
				channel,
				self._args, ", ".join(attrStrings))

	def __getitem__(self, x):
		if type(x) == int:
			return self._args[x]
		elif type(x) == str:
			return self._kwargs[x]
		else:
			raise KeyError(x)

class Remote(Manager):

	def __init__(self, nodes=(), address="0.0.0.0", port=64000):
		Manager.__init__(self)

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

	def __poll__(self, wait=0.01):
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

		if source not in self._nodes:
			self._nodes.append(source)

		try:
			Manager.send(self, event, channel, source)
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
		queue = self._queue

		for i, (event, channel, source) in enumerate(queue[:]):
			try:
				try:
					Manager.send(self, event, channel, source)
				except UnhandledEvent:
					pass

				if len(self._nodes) > 0:
					if source is None:
						source = (socket.gethostname(), self._port,)
					s = pickle.dumps((event, channel, source))
					if len(self._buffer) + len(s) > 8192:
						self.__write__(self._buffer)
						self._buffer = ""
					self._buffer += s
			finally:
				del queue[i]

		if not self._buffer == "":
			self.__write__(self._buffer)
			self._buffer = ""

	def send(self, event, channel, source=None):
		r = Manager.send(self, event, channel, source)
		if not caller() == "flush":
			if source is None:
				source = (socket.gethostname(), self._port,)
			self.__write__(pickle.dumps((event, channel, source)))
		return r
