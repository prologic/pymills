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

	def __new__(cls, *args, **kwargs):
		self = object.__new__(Event)

		self.name = cls.__name__
		self.args = args
		self.kwargs = kwargs

		self.channel = None
		self.target = None

		self.source = None # Used by Bridge
		self.ignore = False # Used by Bridge

		return self

	def __eq__(self, y):
		" x.__eq__(y) <==> x==y"

		attrs = ["name", "args", "kwargs", "channel"]
		r = [getattr(self, a) == getattr(y, a) for a in attrs]
		return False not in r

	def __repr__(self):
		"x.__repr__() <==> repr(x)"

		attrs = ((k, v) for k, v in self.kwargs.items())
		attrStrings = ("%s=%s" % (k, v) for k, v in attrs)
		channel = self.channel or ""
		return "<%s/%s %s {%s}>" % (
				self.name, channel,
				self.args, ", ".join(attrStrings))

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


def send(handlers, event):
	"""send(handlers event) -> None

	Send the given event to the list of handlers.
	If no handlers	are given, raise an UnhandledEvent
	exception. If a handler	return True, return
	immediately and do not allow any other handler to
	process this event.
	"""

	if not handlers:
		raise UnhandledEvent(event)

	for handler in handlers:
		if handler(event, *event.args, **event.kwargs):
			return

from pymills.event.core import Manager, Component, Worker
from pymills.event.bridge import Bridge, DummyBridge
from pymills.event.timers import Timers
from pymills.event.debugger import Debugger

e = Manager()
debugger = Debugger(e)
timers = Timers(e)

__all__ = (
	"e",
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
