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
		self._channels = defaultdict(lambda: [])
		self._channels["global"] = []
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
			return self._channels[channel]
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
			if channel in self._channels:
				if handler not in self._channels[channel]:
					self._channels[channel].append(handler)
					self._channels[channel].sort(cmp=_sortHandlers)
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

		if channel:
			if channel == "global":
				raise EventError("Cannot push to global channel")

		event.channel = channel
		event.target = target
		if (target is not None) and target not in channel:
			channel = "%s:%s" % (target, channel)
			event.channel = channel

		if self.manager == self:
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
				handlers = self.getHandlers("global") + self.getHandlers(channel)
				if handlers == []:
					_queue.remove(event)
					raise UnhandledEvent, event
				try:
					for handler in handlers:
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

		if channel:
			if channel == "global":
				raise EventError("Cannot send to global channel")

		event.channel = channel
		event.target = target
		if (target is not None) and target not in channel:
			channel = "%s:%s" % (target, channel)
			event.channel = channel

		if self.manager == self:
			handlers = self.getHandlers("global") + self.getHandlers(channel)
			if handlers == []:
				raise UnhandledEvent, event
			try:
				for handler in handlers:
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
	def onFOO(self):
		return True

	@listener()
	def onBAR(self):
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
			if self.channel is not None:
				channel = "%s:%s" % (self.channel, handler.channel)
			else:
				channel = handler.channel

			manager.add(handler, channel)

			self._handlers.add(handler)

			if channel in self._channels:
				self._channels[channel].append(handler)
				self._channels[channel].sort(cmp=_sortHandlers)
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
