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

		self.assertTrue(
				filter.onFOO in event.manager.getHandlers("foo"))
		self.assertTrue(
				listener.onFOO in event.manager.getHandlers("foo"))
		self.assertTrue(
				filter.onBAR in event.manager.getHandlers("bar"))
		self.assertTrue(
				listener.onBAR in event.manager.getHandlers("bar"))

		filter.unregister()
		listener.unregister()

		self.assertEquals(len(event.manager.getHandlers()), 0)

	def testComponentLinks(self):
		"""Test Component Links

		Test that components can be linked together and
		events can be sent to linked components.
		"""

		foo = Foo()
		bar = Bar()
		foo + bar

		handlers = foo.getHandlers()
		self.assertTrue(foo.onFOO in handlers)
		self.assertTrue(bar.onBAR in handlers)
		self.assertTrue(foo.onGOTBAR in handlers)

		foo.send(Event(), "foo")
		self.assertTrue(foo.gotbar)

		foo - bar

		handlers = foo.getHandlers()
		self.assertTrue(foo.onFOO in handlers)
		self.assertTrue(bar.onBAR not in handlers)
		self.assertTrue(foo.onGOTBAR in handlers)

	def testWorker(self):
		"""Test Worker

		...
		"""

#		foo = FooWorker(event.manager)

#		r = self.send(Event(), "foo")
#		self.assertEquals(r, ["foo"])

#		foo.stop()
#		foo.unregister()

#		self.assertEquals(self.getHandlers(), [])

	def testEvent(self):
		"""Test Event

		Test new Event construction and that it's associated
		arguments and keyword arguments are stored correctly.
		"""

		e = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")

		self.assertEquals(e.name, "Test")
		self.assertEquals(e.channel, None)
		self.assertEquals(e.target, None)
		self.assertFalse(e.ignore)

		self.assertTrue((1, 2, 3, "foo", "bar") == e.args)

		self.assertEquals(e.kwargs["foo"], "1")
		self.assertEquals(e.kwargs["bar"], "2")

		self.assertEquals(str(e),
				"<Test/ (1, 2, 3, 'foo', 'bar') {foo=1, bar=2}>")

	def testManager(self):
		"""Test Manager

		Test Manager construction and that a global
		channel is created. Test that the event queue is
		empty.
		"""

		self.assertTrue(
				event.manager._channels.has_key("global"))

		self.assertEquals(len(event.manager), 0)

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
		self.assertTrue(
				onFOO in event.manager.getHandlers("global"))
		self.assertTrue(
				onBAR in event.manager.getHandlers("global"))

		event.manager.add(onFOO, "foo")
		event.manager.add(onBAR, "bar")
		self.assertTrue(
				onFOO in event.manager.getHandlers("foo"))
		self.assertTrue(
				onBAR in event.manager.getHandlers("bar"))

		try:
			event.manager.add(onTEST)
		except EventError:
			pass

		self.assertFalse(onTEST in event.manager.getHandlers())

		event.manager.remove(onFOO)
		self.assertTrue(
				onFOO not in event.manager.getHandlers())

		event.manager.remove(onBAR, "bar")
		self.assertTrue(
				onBAR not in event.manager.getHandlers("bar"))
		self.assertTrue(
				onBAR in event.manager.getHandlers("global"))
		event.manager.remove(onBAR)
		self.assertTrue(
				onBAR not in event.manager.getHandlers())

		self.assertEquals(len(event.manager.getHandlers()), 0)

	def testManagerPushFlushSend(self):
		"""Test Manager's push, flush and send

		Test that events can be pushed, fluahsed and that
		the event queue is empty after flushing. Test that
		events can be sent directly without queuing and that
		events cannot be sent to the global channel.

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

		self.assertTrue(onSTOP in event.manager.getHandlers("global"))
		self.assertTrue(onTEST in event.manager.getHandlers("test"))
		self.assertTrue(onFOO in event.manager.getHandlers("test"))
		self.assertTrue(onBAR in event.manager.getHandlers("bar"))
		self.assertEquals(len(event.manager.getHandlers()), 4)

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

		try:
			event.manager.send(Event(), "global")
			self.assertTrue(False)
		except EventError:
			self.assertTrue(True)

		event.manager.send(Test(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		event.manager.send(Test(self, time.time(), stop=True), "test")
		self.assertTrue(self.flag == False)

		event.manager.remove(onSTOP)
		event.manager.remove(onTEST, "test")
		event.manager.remove(onFOO, "test")
		event.manager.remove(onBAR, "bar")

		self.assertEquals(len(event.manager.getHandlers()), 0)

def suite():
	return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
	unittest.main()
