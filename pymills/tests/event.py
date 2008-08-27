# Module:	event
# Date:		23rd June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Event Test Suite

Test all functionality of the event library.
"""

import unittest

from pymills import event
from pymills.event import *

class Test(Event): pass

class FilterComponent(Component):

	@filter("foo")
	def onFOO(self, msg=""):
		return True

	@filter("bar")
	def onBAR(self, msg=""):
		if msg.lower() == "hello world":
			return True

class ListenerComponent(Component):

	@listener("foo")
	def onFOO(self, test, msg=""):
		if msg.lower() == "start":
			self.push(Test(msg="foo"), "foo")

	@listener("bar")
	def onBAR(self, test, msg=""):
		if msg.lower() == "test":
			self.push(Test(msg="hello world"), event._channel)

class Foo(Component):

	gotbar = False

	@listener("foo")
	def onFOO(self):
		self.send(Test(), "bar")

	@listener("gotbar")
	def onGOTBAR(self):
		self.gotbar = True

class Bar(Component):

	@listener("bar")
	def onBAR(self):
		self.send(Test(), "gotbar")

class FooWorker(Worker):

	@listener("foo")
	def onFOO(self):
		return "foo"

class EventTestCase(unittest.TestCase):

	def testComponentSetup(self):
		"""Test Component Setup

		Tests that filters and listeners of a Component are
		automatically added to the event manager instnace
		given.
		"""

		filter = FilterComponent()
		event.manager += filter
		listener = ListenerComponent()
		event.manager += listener

		self.assertTrue(filter.onFOO in event.manager["foo"])
		self.assertTrue(listener.onFOO in event.manager["foo"])
		self.assertTrue(filter.onBAR in event.manager["bar"])
		self.assertTrue(listener.onBAR in event.manager["bar"])

		filter.unregister()
		listener.unregister()

		self.assertEquals(len(event.manager._handlers), 0)

	def testTargetsAndChannels(self):
		"""Test Components, Targets and Channels

		Test that Components can be set up with a channel
		and that event handlers of that Component work
		correctly. That is, Components that have their
		own channel, have their own global channel and
		each channel is unique to that Component.
		"""

		class Foo(Component):

			channel = "foo"

			flag = False

			@filter()
			def onALL(self, event, *args, **kwargs):
				self.flag = True
				return True

			@listener("foo")
			def onFOO(self):
				self.flag = False

		class Bar(Component):

			flag = False

			@listener("bar")
			def onBAR(self):
				self.flag = True

		foo = Foo()
		bar = Bar()
		event.manager += foo
		event.manager += bar

		event.manager.send(Event(), "foo", foo.channel)
		self.assertTrue(foo.flag)
		event.manager.send(Event(), "bar")
		self.assertTrue(bar.flag)

		foo.unregister()
		bar.unregister()

	def testComponentLinks(self):
		"""Test Component Links

		Test that components can be linked together and
		events can be sent to linked components.
		"""

		foo = Foo()
		bar = Bar()
		foo + bar

		self.assertTrue(foo.onFOO in foo._handlers)
		self.assertTrue(bar.onBAR in foo._handlers)
		self.assertTrue(foo.onGOTBAR in foo._handlers)

		foo.send(Event(), "foo")
		self.assertTrue(foo.gotbar)

		foo - bar

		self.assertTrue(foo.onFOO in foo._handlers)
		self.assertTrue(bar.onBAR not in foo._handlers)
		self.assertTrue(foo.onGOTBAR in foo._handlers)

	def testEvent(self):
		"""Test Event

		Test new Event construction and that it's associated
		arguments and keyword arguments are stored correctly.
		"""

		e = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")

		self.assertEquals(e.__class__.__bases__, (object,))
		self.assertEquals(e.name, "Test")
		self.assertEquals(e.channel, None)
		self.assertEquals(e.target, None)
		self.assertFalse(e.ignore)

		self.assertTrue((1, 2, 3, "foo", "bar") == e.args)

		self.assertEquals(e.kwargs["foo"], "1")
		self.assertEquals(e.kwargs["bar"], "2")

		self.assertEquals(str(e),
				"<Test/ (1, 2, 3, foo, bar, foo=1, bar=2)>")

	def testManager(self):
		"""Test Manager

		Test Manager construction. Test that the event queue is
		empty.
		"""

		self.assertEquals(len(event.manager), 2)
		self.assertEquals(len(event.manager._handlers), 0)

	def testManagerAddRemove(self):
		"""Test Manager.add & Manager.remove

		Test that filters and listeners can be added to
		the global channel. Test that filters and listeners
		can be added to specific channels. Test that
		non-filters and non-listeners cannot be added to any
		channel and raises an EventError. Test that filters
		and listeners can be removed from all channels.
		Test that filters and listeners can be removed from
		a specific channel.
		"""

		@filter("foo")
		def onFOO():
			pass

		@listener("bar")
		def onBAR():
			pass

		def onTEST():
			pass

		event.manager.add(onFOO)
		event.manager.add(onBAR)
		self.assertTrue(onFOO in event.manager.channels["*"])
		self.assertTrue(onBAR in event.manager.channels["*"])

		event.manager.add(onFOO, "foo")
		event.manager.add(onBAR, "bar")
		self.assertTrue(onFOO in event.manager["foo"])
		self.assertTrue(onBAR in event.manager["bar"])

		try:
			event.manager.add(onTEST)
		except EventError:
			pass

		self.assertFalse(onTEST in event.manager.channels["*"])

		event.manager.remove(onFOO)
		self.assertTrue(onFOO not in event.manager._handlers)

		event.manager.remove(onBAR, "bar")
		self.assertTrue(onBAR not in event.manager["bar"])
		self.assertTrue(onBAR in event.manager.channels["*"])
		event.manager.remove(onBAR)
		self.assertTrue(onBAR not in event.manager._handlers)

		self.assertEquals(len(event.manager._handlers), 0)

	def testManagerPushFlushSend(self):
		"""Test Manager's push, flush and send

		Test that events can be pushed, fluahsed and that
		the event queue is empty after flushing. Test that
		events can be sent directly without queuing.

		Test that Event._channel, Event._time and
		Event._source are set appropiately.

		Test that a filter will filter an event and prevent
		any further processing of this event.
		"""

		import time

		self.flag = False
		self.foo = False

		@listener("test")
		def onTEST(test, time, stop=False):
			test.flag = True

		@listener("test")
		def onFOO(test, time, stop=False):
			test.foo = True

		@listener("bar")
		def onBAR(test, time):
			pass

		@filter()
		def onSTOP(test, time, stop=False):
			return stop

		event.manager.add(onSTOP)
		event.manager.add(onTEST, "test")
		event.manager.add(onFOO, "test")
		event.manager.add(onBAR, "bar")

		self.assertTrue(onSTOP in event.manager.channels["*"])
		self.assertTrue(onTEST in event.manager["test"])
		self.assertTrue(onFOO in event.manager["test"])
		self.assertTrue(onBAR in event.manager["bar"])
		self.assertEquals(len(event.manager._handlers), 4)

		event.manager.push(Test(self, time.time()), "test")
		event.manager.flush()
		self.assertTrue(self.flag == True)
		self.flag = False
		self.assertTrue(self.foo == True)
		self.foo = False

		self.assertEquals(len(event.manager), 0)

		event.manager.send(Test(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		event.manager.send(Test(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		event.manager.send(Test(self, time.time(), stop=True), "test")
		self.assertTrue(self.flag == False)

		event.manager.remove(onSTOP)
		event.manager.remove(onTEST, "test")
		event.manager.remove(onFOO, "test")
		event.manager.remove(onBAR, "bar")

		self.assertEquals(len(event.manager._handlers), 0)

def suite():
	return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
	unittest.main()
