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

Channels are automatically registered by each Component
that is linked to an EventManager. All methods/functions
of the component that are marked with a filter or listener
decorator are added to the appropiate channel of the
event manager given to it.

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
import select
import inspect
import cPickle as pickle

from datatypes import CaselessDict

class EventError(Exception):
	"Event Error"

class UnhandledEvent(EventError):
	"Unhandled Event Error"

	def __init__(self, event, channel):
		EventError.__init__(self, event, channel)

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
			if hasattr(self, "__channelPrefix__"):
				self.event.add(handler, "%s:%s" % (
					self.__channelPrefix__,
					handler.channel))
			else:
				self.event.add(handler, handler.channel)

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
			self.event.remove(handler, handler.channel)

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
	
	def __getitem__(self, x):
		if type(x) == int:
			return self._args[x]
		elif type(x) == str:
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

class EventManager(object):
	"""EventManager() -> new event manager

	Create a new event manager which manages events.
	If server=True, this will listen on the default port
	of 64000 allowing events to be to other connected
	remote event managers.
	"""

	def __init__(self):
		"initializes x; see x.__class__.__doc__ for signature"

		self._filters = CaselessDict({"global": []})
		self._listeners = CaselessDict({"global": []})
		self._queue = []

	def __len__(self):
		return len(self._queue)

	def add(self, callable, *channels):
		"""E.add(callable, *channels) -> None

		Add a new filter or listener to the event manager
		adding it to all channels specified. if no channels
		are given, add it to the global channel.
		"""

		if len(channels) == 0:
			channels = ["global"]

		for channel in channels:

			if hasattr(callable, "filter"):
				container = self._filters
			elif hasattr(callable, "listener"):
				container = self._listeners
			else:
				raise EventError("Given callable '%s' is" \
						"not a filter or listener" % callable)

			if container.has_key(channel):
				container[channel].append(callable)
			else:
				container[channel] = [callable]
	
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
			keys = self._filters.keys() + self._listeners.keys()
		else:
			keys = channels

		for channel in keys:

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
						"Channel %s not found" % channel)

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

		queue = self._queue

		for event, channel, source in queue[:]:
			try:
				self.send(event, channel, source)
			except:
				raise
			finally:
				queue.remove((event, channel, source))

	def send(self, event, channel, source=None):
		"""E.send(event, channel, source=None) -> None

		Send the given event to listeners on the given channel.
		source is expected to be an object.

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
						"Error with filter/listener '%s': %s" % (
							callable, e))

		if source is not None and hasattr(source, "__channelPrefix__"):
			channel = "%s:%s" % (source.__channelPrefix__, channel)

		if channel == "global":
			raise EventError(
					"You cannot send events to the global channel")

		event._time = time.time()
		event._source = source
		event._channel = channel

		filters = self._filters.get("global", []) + \
				self._filters.get(channel, [])
		listeners =	self._listeners.get("global", []) + \
				self._listeners.get(channel, [])

		if filters == [] and listeners == []:
			raise UnhandledEvent(event, channel)

		for filter in filters:
			try:
				halt, newEvent = call(filter, event)
			except TypeError:
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

class RemoteManager(EventManager):

	def __init__(self, nodes=[]):
		EventManager.__init__(self)

		self._nodes = nodes

		self._ssock = socket.socket(
				socket.AF_INET,
				socket.SOCK_DGRAM)
		self._ssock.setsockopt(
				socket.SOL_SOCKET,
				socket.SO_REUSEADDR,
				1)
		self._ssock.setblocking(False)
		self._ssock.bind(("0.0.0.0", 64000))

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

	def __poll__(self, wait=0.001):
		try:
			r, w, e = select.select([self._ssock], [], [], wait)
			return not r == []
		except socket.error, error:
			raise
			self.__close__()
			return False

	def __read__(self, bufsize=512):
		try:
			data, addr = self._ssock.recvfrom(bufsize)
		except socket.error, e:
			raise
			self.__close__()
	
		if addr[0] not in self._nodes:
			self._nodes.append(addr[0])

		event, channel = pickle.loads(data)
		EventManager.send(self, event, channel)

	def __close__(self):
		self._ssock.shutdown(2)
		self._ssock.close()
		self._csock.shutdown(2)
		self._csock.close()
	
	def __write__(self, data):
		for node in self._nodes:
			bytes = self._csock.sendto(data, (node, 64000))
			if bytes < len(data):
				raise EventError("Couldn't send event to %s" % str(node))

	def process(self):
		if self.__poll__():
			self.__read__()

	def send(self, event, channel, source=None):
		r = EventManager.send(self, event, channel, source)
		if not self._nodes == []:
			self.__write__(pickle.dumps((event, channel)))
		return r
