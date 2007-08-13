# Module:	event
# Date:		23rd June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Event Test Suite

Test all functionality of the event library.
"""

import unittest
from pprint import pprint

from pymills.event import *

class FilterComponent(Component):

	@filter("foo")
	def onFOO(self, event, msg=""):
		return False, Event(msg.lower())

	@filter("bar")
	def onBAR(self, event, msg=""):
		if msg.lower() == "hello world":
			return True, event
		else:
			return False, event
	
class ListenerComponent(Component):

	@listener("foo")
	def onFOO(self, event, test, msg=""):
		if msg.lower() == "start":
			self.event.push(
					Event(msg="foo"),
					event._channel)

	@listener("bar")
	def onBAR(self, event, test, msg=""):
		if msg.lower() == "test":
			self.event.push(
					Event(msg="hello world"),
					event._channel)

class Foo(Component):

	@listener("foo")
	def onFOO(self, event):
		return self.send(Event(), "bar")

class Bar(Component):

	@listener("bar")
	def onBAR(self, event):
		return "bar"

class FooWorker(Worker):

	@listener("foo")
	def onFOO(self, event):
		return "foo"

class EventTestCase(unittest.TestCase):

	def setUp(self):
		self.event = EventManager()

	def tearDown(self):
		pass
	
	def testComponentIDs(self):
		"""Test Component IDs

		Test that components are singletons and that at most
		one instance of any Component type can be instantiated.
		"""

		class ComponentA(Component):
			pass

		class ComponentB(Component):
			pass

		x = Component(self.event)
		y = Component(self.event)

		a = ComponentA(self.event)
		b = ComponentB(self.event)

		self.assertEquals(id(x), id(y))
		self.assertNotEquals(id(a), id(b))

		self.assertEquals(self.event.getHandlers(), [])

	def testComponentSetup(self):
		"""Test Component Setup

		Tests that filters and listeners of a Component are
		automatically added to the event manager instnace
		given.
		"""

		filter = FilterComponent(self.event)
		listener = ListenerComponent(self.event)

		self.assertTrue(
				filter.onFOO in self.event.getHandlers("foo"))
		self.assertTrue(
				listener.onFOO in self.event.getHandlers("foo"))
		self.assertTrue(
				filter.onBAR in self.event.getHandlers("bar"))
		self.assertTrue(
				listener.onBAR in self.event.getHandlers("bar"))

		filter.unregister()
		listener.unregister()

		self.assertEquals(self.event.getHandlers(), [])

	def testComponentLinks(self):
		"""Test Component Links

		Test that components can be linked together and
		events can be sent to linked components.
		"""

		foo = Foo(self.event)
		bar = Bar(self.event)

		foo.link(bar)

		self.assertTrue(bar.onBAR in foo.getHandlers())

		r = self.event.send(Event(), "foo")
		self.assertEquals(r, [["bar"]])

		foo.unregister()
		bar.unregister()

		self.assertEquals(self.event.getHandlers(), [])

	def testWorker(self):
		"""Test Worker

		...
		"""

		foo = FooWorker(self.event)

		r = self.event.send(Event(), "foo")
		self.assertEquals(r, ["foo"])

		foo.stop()
		foo.unregister()

		self.assertEquals(self.event.getHandlers(), [])

	def testEvent(self):
		"""Test Event

		Test new Event construction and that it's associated
		arguments and keyword arguments are stored correctly.
		"""

		a = Event(1, 2, 3, "foo", "bar", foo="1", bar="2")

		self.assertTrue(1 in a._args)
		self.assertTrue(2 in a._args)
		self.assertTrue(3 in a._args)
		self.assertTrue("foo" in a._args)
		self.assertTrue("bar" in a._args)

		self.assertEquals(a._kwargs["foo"], "1")
		self.assertEquals(a._kwargs["bar"], "2")

		self.assertEquals(a.foo, "1")
		self.assertEquals(a.bar, "2")

		self.assertEquals(str(a),
				"<Event/None (1, 2, 3, 'foo', 'bar') {foo=1, bar=2}>")

	def testEventManager(self):
		"""Test EventManager

		Test EventManager construction and that a global
		channel is created. Test that the event queue is
		empty.
		"""

		self.assertTrue(
				self.event._handlers.has_key("global"))

		self.assertEquals(len(self.event), 0)

	def testEventManagerAddRemove(self):
		"""Test EventManager.add & EventManager.remove

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

		self.event.add(onFOO)
		self.event.add(onBAR)
		self.assertTrue(
				onFOO in self.event.getHandlers("global"))
		self.assertTrue(
				onBAR in self.event.getHandlers("global"))

		self.event.add(onFOO, "foo")
		self.event.add(onBAR, "bar")
		self.assertTrue(
				onFOO in self.event.getHandlers("foo"))
		self.assertTrue(
				onBAR in self.event.getHandlers("bar"))

		try:
			self.event.add(onTEST)
		except EventError:
			pass

		self.assertFalse(onTEST in self.event.getHandlers())

		self.event.remove(onFOO)
		self.assertTrue(
				onFOO not in self.event.getHandlers())

		self.event.remove(onBAR, "bar")
		self.assertTrue(
				onBAR not in self.event.getHandlers("bar"))
		self.assertTrue(
				onBAR in self.event.getHandlers("global"))
		self.event.remove(onBAR)
		self.assertTrue(
				onBAR not in self.event.getHandlers())

		self.assertEquals(self.event.getHandlers(), [])

	def testEventManagerPushFlushSend(self):
		"""Test EventManager's push, flush and send

		Test that events can be pushed, fluahsed and that
		the event queue is empty after flushing. Test that
		events can be sent directly without queuing and that
		events cannot be sent to the global channel.

		Test that Event._channel, Event._time and
		Event._source are set appropiately.

		Test that a filter will filter an event and prevent
		any further processing of this event.

		Test that events sent directly to listeners can have
		a return value from that listener. The return value
		should be a list of return values from all listeners
		listening to the given channel for that event.
		"""

		import time

		self.flag = False
		self.foo = False

		@filter()
		def onCHECK(event, test, time):
			test.assertTrue(
					hasattr(event, "_time") and
					type(event._time) == float and
					int(event._time) == int(time))
			test.assertTrue(hasattr(event, "_channel"))
			test.assertTrue(hasattr(event, "_source"))
			return False, event

		@listener("test")
		def onTEST(test, time):
			test.flag = True
			return "test"

		@listener("test")
		def onFOO(test, time):
			test.foo = True
			return "foo"
		
		@listener("bar")
		def onBAR(test, time):
			return "bar"

		@filter()
		def onSTOP(event, test, time, stop=False):
			return stop, event

		self.event.add(onSTOP)
		self.event.add(onCHECK)
		self.event.add(onTEST, "test")
		self.event.add(onFOO, "test")
		self.event.add(onBAR, "bar")

		self.assertTrue(onSTOP in self.event.getHandlers("global"))
		self.assertTrue(onCHECK in self.event.getHandlers("global"))
		self.assertTrue(onTEST in self.event.getHandlers("test"))
		self.assertTrue(onFOO in self.event.getHandlers("test"))
		self.assertTrue(onBAR in self.event.getHandlers("bar"))
		self.assertEquals(len(self.event.getHandlers()), 5)

		self.event.push(Event(self, time.time()), "test")
		self.event.flush()
		self.assertTrue(self.flag == True)
		self.flag = False
		self.assertTrue(self.foo == True)
		self.foo = False

		self.assertEquals(len(self.event), 0)

		self.event.send(Event(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		try:
			self.event.send(Event(), "global")
			self.assertTrue(False)
		except EventError:
			self.assertTrue(True)

		self.event.send(Event(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		self.event.send(Event(self, time.time(), stop=True),
				"test")
		self.assertTrue(self.flag == False)

		r = self.event.send(Event(self, time.time()), "test")
		self.assertEquals(r[0], "test")
		self.assertEquals(r[1], "foo")

		self.assertEquals(
				self.event.send(Event(self, time.time()), "bar"),
				["bar"])

		self.event.remove(onSTOP)
		self.event.remove(onCHECK)
		self.event.remove(onTEST, "test")
		self.event.remove(onFOO, "test")
		self.event.remove(onBAR, "bar")

		self.assertEquals(self.event.getHandlers(), [])

def suite():
	return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
	unittest.main()
