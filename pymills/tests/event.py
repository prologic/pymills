# Filename: event.py
# Module:	event
# Date:		23rd June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Event Test Suite

...
"""

import unittest

from pymills.event import filter, listener, Component, \
		Event, EventError, FilteredEvent, EventManager

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

class EventTestCase(unittest.TestCase):

	def setUp(self):
		self.event = EventManager()

	def tearDown(self):
		pass
	
	def testComponentIDs(self):
		"""Test event.Component

		1. Test that there can only be at most one instance of
		   a single component
		2. Test that sub-classes of Component can be instantiated
		3. Test that any sub-class instances also cannot be
		   instantiated more than once
		"""

		#1

		class ComponentA(Component):
			pass

		class ComponentB(Component):
			pass

		x = Component(self.event)
		y = Component(self.event)

		#2
		a = ComponentA(self.event)
		b = ComponentB(self.event)

		#1
		self.assertEquals(id(x), id(y))

		#3
		self.assertNotEquals(id(a), id(b))

	def testComponentSetup(self):
		"""Test event.Componoent

		1. Test that any filters and listeners found in a
		   Component are automatically added to the EventManager
		2. Test that channels are added for these filters and
		   listeners automatically
		"""

		#1

		filter = FilterComponent(self.event)
		listener = ListenerComponent(self.event)

		#2
		self.assertTrue(
				self.event._handlers.has_key("foo"))
		self.assertTrue(
				self.event._handlers.has_key("bar"))

	def testEvent(self):
		"""Test event.Event

		1. Test that args given are stored
		2. Test that kwargs given are stored
		3. Test that kwargs also become the instance attributes
		4. Test the str/repr string
		5. Test that __str__ and __repr__ return the same thing
		"""

		import time

		a = Event(1, 2, 3, "foo", "bar", foo="1", bar="2")

		#1
		self.assertTrue(1 in a._args)
		self.assertTrue(2 in a._args)
		self.assertTrue(3 in a._args)
		self.assertTrue("foo" in a._args)
		self.assertTrue("bar" in a._args)

		#2
		self.assertEquals(a._kwargs["foo"], "1")
		self.assertEquals(a._kwargs["bar"], "2")

		#3
		self.assertEquals(a.foo, "1")
		self.assertEquals(a.bar, "2")

		#4
		self.assertEquals(str(a),
				"<Event/None (1, 2, 3, 'foo', 'bar') {foo=1, bar=2}>")

		#5
		self.assertEquals(str(a), repr(a))
	
	def testEventManager(self):
		"""Test EventManager

		1. Test that there is a global channel setup
		2. Test that the event queue is empty
		"""

		#1
		self.assertTrue(
				self.event._handlers.has_key("global"))

		#2
		self.assertTrue(self.event._queue == [])

	def testEventManagerAddRemove(self):
		"""Test EventManager.add & EventManager.remove

		1. Test that filters/listeners can be added to the
		   global channel
		2. Test that filters/listeners can be added to a
		   specific channel
		3. Test that non-filters/listeners cannot be added
		   and raises an EventError
		4. Test that filters/listeners can be removed from
		   all channels
		5. Test that filters/listeners can be removed from
		   a specific channel
		"""

		@filter("foo")
		def onFOO():
			pass

		@listener("bar")
		def onBAR():
			pass

		def onTEST():
			pass

		#1
		self.event.add(onFOO)
		self.event.add(onBAR)
		self.assertTrue(
				onFOO in self.event._handlers["global"])

		#2
		self.event.add(onFOO, "test")
		self.event.add(onBAR, "test")
		self.assertTrue(
				onFOO in self.event._handlers["test"])

		#3
		try:
			self.event.add(onTEST)
			self.assertFalse(False)
		except EventError:
			self.assertTrue(True)

		#4
		self.event.remove(onFOO)
		self.assertTrue(
				onFOO not in self.event._handlers.values())

		#5
		self.event.remove(onBAR, "test")
		self.assertTrue(
				onBAR in self.event._handlers["global"])

	def testEventManagerPushFlushSend(self):
		"""Test EventManager's push, flush and send

		1. Test push
		2. Test flush
		3. Test that the event queue is empty after flushing
		4. Test send
		5. Test that events cannot be sent to the global
		   channel
		6. Test that _channel and _time are set on
		   the event
		7 Test that a filter actually can stop further event
		   processing
		"""

		import time

		self.flag = False
		self.foo = False

		@filter()
		def onCHECK(event, test, time):
			#6
			test.assertTrue(
					hasattr(event, "_time") and
					type(event._time) == float and
					int(event._time) == int(time))
			test.assertTrue(hasattr(event, "_channel"))
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

		#1 & #2
		self.event.push(Event(self, time.time()), "test")
		self.event.flush()
		self.assertTrue(self.flag == True)
		self.flag = False
		self.assertTrue(self.foo == True)
		self.foo = False

		#3
		self.assertTrue(self.event._queue == [])

		#4
		self.event.send(Event(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		#5
		try:
			self.event.send(Event(), "global")
			self.assertFalse(False)
		except EventError:
			self.assertTrue(True)

		#6
		self.event.send(Event(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		#7
		try:
			self.event.send(Event(self, time.time(), stop=True),
					"test")
		except FilteredEvent:
			pass
		self.assertTrue(self.flag == False)

		r = self.event.send(Event(self, time.time()), "test")
		self.assertEquals(r[0], "test")
		self.assertEquals(r[1], "foo")

		self.assertEquals(
				self.event.send(Event(self, time.time()), "bar"),
				["bar"])

def suite():
	return unittest.makeSuite(EventTestCase, "test")


if __name__ == "__main__":
	unittest.main()
