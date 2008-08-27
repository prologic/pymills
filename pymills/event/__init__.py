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

from pymills.event.errors import EventError
from pymills.event.core import filter, listener, Event
from pymills.event.core import Manager, Component, Worker

from pymills.event.debugger import Debugger
from pymills.event.bridge import Bridge, DummyBridge

manager = Manager()
debugger = Debugger()

__all__ = (
	"manager",
	"debugger",
	"filter",
	"listener",
	"Event",
	"EventError",
	"Manager",
	"Component",
	"Worker",
	"DummyBridge",
	"Bridge",
	"Debugger")
