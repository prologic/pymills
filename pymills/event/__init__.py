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

Event handlers that do not specify a channel, will receive
'''all''' events. Global Event handlers are always processed
before any channels.

WHen an event is sent to either a filter or listener's
handler, the event manager will '''try''' to apply the
event's date (args and kwargs) to that handler. The handler
of a filter or listener thus becomes an API which must be
conformed to.

If any error occurs, an Error is raised with the
appropiate message.

A Component is an object that holds a copy of the
Manager instnace and automatically sets up any
filters/listeners found in the class. Filter/listener
methods must start with "on" and must have the
attribute "filter" or "listener" set to True. All
components are singletons, that is they can only be
instantiated once.
"""

from inspect import getargspec
from threading import enumerate as threads


class EventError(Exception):
	"Event Error"


class UnhandledEvent(EventError):
	"Unhandled Event Error"

	def __init__(self, event):
		super(UnhandledEvent, self).__init__(event)


class Event(object):
	"""Event(*args, **kwargs) -> new event object

	Create a new event object populating it with the given
	list of arguments and dictionary of keyword arguments.
	"""

	channel = None
	target = None

	source = None # Used by Bridge
	ignore = False # Used by Bridge

	def __init__(self, *args, **kwargs):
		self.name = self.__class__.__name__
		self.args = args
		self.kwargs = kwargs

	def __eq__(self, y):
		" x.__eq__(y) <==> x==y"

		attrs = ["name", "args", "kwargs", "channel", "target"]
		r = [getattr(self, a) == getattr(y, a) for a in attrs]
		return False not in r

	def __repr__(self):
		"x.__repr__() <==> repr(x)"

		if self.channel is not None and self.target is not None:
			channelStr = "%s:%s" % (self.target, self.channel)
		elif self.channel is not None:
			channelStr = self.channel
		else:
			channelStr = ""
		argsStr = ", ".join([("%s" % arg) for arg in self.args])
		kwargsStr = ", ".join(
				[("%s=%s" % kwarg) for kwarg in self.kwargs.iteritems()])
		return "<%s/%s (%s, %s)>" % (self.name, channelStr, argsStr, kwargsStr)

	def __getitem__(self, x):
		"x.__getitem__(y) <==> x[y]"

		if type(x) == int:
			return self.args[x]
		elif type(x) == str:
			return self.kwargs[x]
		else:
			raise KeyError(x)


def workers():
	"""workers() -> list of workers

	Get the current list of active Worker's
	"""

	return [thread for thread in threads() if isinstance(thread, Worker)]


def filter(channel=None):
	"Decorator function for a filter"

	def decorate(f):
		f.type = "filter"
		f.channel = channel
		f.args = getargspec(f)[0]
		if f.args and f.args[0] == "self":
			del f.args[0]
		return f
	return decorate


def listener(channel=None):
	"Decorator function for a listener"

	def decorate(f):
		f.type = "listener"
		f.channel = channel
		f.args = getargspec(f)[0]
		if f.args and f.args[0] == "self":
			del f.args[0]
		return f
	return decorate


from pymills.event.core import Manager, Component, Worker
from pymills.event.bridge import Bridge, DummyBridge
from pymills.event.debugger import Debugger

manager = Manager()
debugger = Debugger()

__all__ = (
	"manager",
	"debugger",
	"filter",
	"listener",
	"Event",
	"EventError",
	"UnhandledEvent",
	"Manager",
	"Component",
	"Worker",
	"DummyBridge",
	"Bridge",
	"Debugger")
