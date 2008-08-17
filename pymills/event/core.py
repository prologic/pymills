# Module:	core
# Date:		2nd April 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Core

Core components and managers.
"""

from time import sleep
from threading import Thread
from collections import defaultdict
from inspect import getmembers, ismethod

from pymills.event import EventError, UnhandledEvent


def _sortHandlers(x, y):
	if x.type == "filter" and y.type == "filter":
		return 0
	elif x.type == "filter":
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

		self._queue = []
		self._global = set()
		self._handlers = set()

		self.manager = self
		self.channels = defaultdict(lambda: [])

	def __getitem__(self, x):
		return self.channels[x]

	def __len__(self):
		return len(self._queue)

	def __add__(self, y):
		y.register(self.manager)
		return self
	
	def __iadd__(self, y):
		if isinstance(self, Manager):
			y.register(self.manager)
			return self
		else:
			raise TypeError(
					"unsupported operand type(s) for +: '%s' and '%s'" % (
						self, y))

	def __sub__(self, y):
		y.unregister()
		return self

	def handlers(self, channel):
		for handler in self._global:
			yield handler

		if ":" in channel:
			x = "%s:*" % channel.split(":")[0]
			for handler in self.channels[x]:
				yield handler

		for handler in self.channels[channel]:
			yield handler

	def add(self, handler, channel=None):
		"""E.add(handler, channel) -> None

		Add a new filter or listener to the event manager
		adding it to the given channel. If no channel is
		given, add it to the global channel.
		"""

		if getattr(handler, "type", None) not in ["filter", "listener"]:
			raise EventError("%s is not a filter or listener" % handler)

		self._handlers.add(handler)

		if channel is None:
			self._global.add(handler)
		else:
			if channel in self.channels:
				if handler not in self.channels[channel]:
					self.channels[channel].append(handler)
					self.channels[channel].sort(cmp=_sortHandlers)
			else:
				self.channels[channel] = [handler]

	def remove(self, handler, channel=None):
		"""E.remove(handler, channel=None) -> None

		Remove the given filter or listener from the
		event manager removing it from the given channel.
		if channel is None, remove it from the global
		channel. This will succeed even if the specified
		handler has already been removed.
		"""

		if channel is None:
			if handler in self._global:
				self._global.remove(handler)
			keys = self.channels.keys()
		else:
			keys = [channel]

		if handler in self._handlers:
			self._handlers.remove(handler)

		for channel in keys:
			if handler in self.channels[channel]:
				self.channels[channel].remove(handler)


	def push(self, event, channel, target=None):
		"""E.push(event, channel, target=None) -> None

		Push the given event onto the given channel.
		This will queue the event up to be processed later
		by flushEvents. If target is given, the event will
		be queued for processing by the component given by
		target.
		"""

		if self.manager == self:
			event.channel = channel
			event.target = target
			self._queue.append(event)
		else:
			self.manager.push(event, channel, target)

	def flush(self):
		"""E.flushEvents() -> None

		Flush all events waiting in the queue.
		Any event waiting in the queue will be sent out
		to filters/listeners.
		"""

		if self.manager == self:
			_queue = self._queue
			queue = _queue[:]
			for event in queue:
				channel = event.channel
				target = event.target
				if target is not None:
					channel = "%s:%s" % (target, channel)
				if not self._global and channel not in self.channels:
					_queue.remove(event)
					raise UnhandledEvent, event
				try:
					for handler in self.handlers(channel):
						if handler.args:
							if handler.args[0] in ["e", "evt", "event"]:
								if handler(event, *event.args, **event.kwargs):
									break
							else:
								if handler(*event.args, **event.kwargs):
									break
						else:
							if handler():
								break
				except:
					raise
				finally:
					_queue.remove(event)
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
			event.channel = channel
			event.target = target
			if target is not None:
				channel = "%s:%s" % (target, channel)
			if not self._global and channel not in self.channels:
				raise UnhandledEvent, event
			try:
				for handler in self.handlers(channel):
					if handler.args:
						if handler.args[0] in ["e", "evt", "event"]:
							if handler(event, *event.args, **event.kwargs):
								break
						else:
							if handler(*event.args, **event.kwargs):
								break
					else:
						if handler():
							break
			except:
				raise
		else:
			self.manager.send(event, channel, target)


class Component(Manager):
	"""Component() -> new component object

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
	def onFOO(self):
		return True

	@listener()
	def onBAR(self):
		print event
	}
	"""

	channel = None

	def __init__(self, *args, **kwargs):
		super(Component, self).__init__(*args, **kwargs)

		self.channel = kwargs.get("channel", self.channel)
		self.register(self)

	def __del__(self):
		self.unregister()

	def register(self, manager):
		self.manager = manager

		handlers = [x[1] for x in getmembers(
			self, lambda x: ismethod(x) and
			callable(x) and x.__name__.startswith("on") and
			(getattr(x, "type", None) in ["filter", "listener"]))]

		for handler in handlers:
			if self.channel is not None:
				channel = "%s:%s" % (self.channel, handler.channel or "*")
			else:
				channel = handler.channel

			self.manager.add(handler, channel)

	def unregister(self):
		"""C.unregister() -> None

		Unregister all listeners/filters associated with
		this component
		"""

		for handler in self._handlers.copy():
			self.manager.remove(handler)

		self.manager = self


class Worker(Component, Thread):

	def __init__(self, *args, **kwargs):
		super(Worker, self).__init__(*args, **kwargs)

		start = kwargs.get("start", False)
		if start:
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
