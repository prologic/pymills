# Filename: event.py
# Module:	event
# Date:		23rd June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Event Test Suite

...
"""

import os
import time
import unittest

from pymills.event import *

class FilterComponent(Component):

	@filter("Foo")
	def onFoo(self, event, msg=""):
		return False, Event(msg.lower())

	@filter("Bar")
	def onBar(self, event, msg=""):
		if msg.lower() == "hello world":
			return True, event
		else:
			return False, event
	
class ListenerComponent(Component):

	@listener("Foo")
	def onFoo(self, event, test, msg=""):
		if msg.lower() == "start":
			self.event.pushEvent(
					Event(msg="foo"),
					event._channel)

	@listener("Bar")
	def onBar(self, event, test, msg=""):
		if msg.lower() == "test":
			self.event.pushEvent(
					Event(msg="hello world"),
					event._channel)

class EventTestCase(unittest.TestCase):

	def setUp(self):
		self.event = EventManager()

	def tearDown(self):
		pass
	
	def testEventError(self):
		"""Test event.EvenerError

		1. Test that raising an exception of type EventError
		   works and a message is shown
		"""

		try:
			raise EventError("test")
		except EventError, msg:
			#1
			self.assertEquals(str(msg), "test")

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
		3. Test that the filters/listeners are being added to
		   the right container
		"""

		#1

		filter = FilterComponent(self.event)
		listener = ListenerComponent(self.event)

		#2
		fooChannel = self.event.getChannelID("Foo")
		barChannel = self.event.getChannelID("Bar")

		#2
		self.assertTrue(fooChannel is not None)
		self.assertTrue(barChannel is not None)

		#3
		self.assertTrue(
				filter.onFoo in 
				self.event._filters[fooChannel])
		self.assertTrue(
				filter.onBar in
				self.event._filters[barChannel])
		self.assertTrue(
				listener.onFoo in
				self.event._listeners[fooChannel])
		self.assertTrue(
				listener.onBar in
				self.event._listeners[barChannel])
	
	def testEvent(self):
		"""Test event.Event

		1. Test that args given are stored
		2. Test that a timestamp is inserted
		3. Test that kwargs given are stored
		4. Test that kwargs also become the instance attributes
		5. Test the str/repr string
		6. Test that __str__ and __repr__ return the same thing
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
		self.assertEquals(int(a._time), int(time.time()))

		#3
		self.assertEquals(a._kwargs["foo"], "1")
		self.assertEquals(a._kwargs["bar"], "2")

		#4
		self.assertEquals(a.foo, "1")
		self.assertEquals(a.bar, "2")

		#5
		self.assertEquals(str(a),
				"<Event (1, 2, 3, 'foo', 'bar') {bar=2, foo=1}>")

		#6
		self.assertEquals(str(a), repr(a))
	
	def testEventManager(self):
		"""Test EventManager

		1. Test that there is a global channel setup
		2. Test that the filter and listener containers
		   have this global channel
		3. Test that the event queue is empty
		"""

		#1
		channel = self.event.getChannelID("global")
		self.assertTrue(
				channel is not None and type(channel) == int)

		#2
		self.assertTrue(
				self.event._filters.has_key(channel))
		self.assertTrue(
				self.event._listeners.has_key(channel))

		#3
		self.assertTrue(self.event._queue == [])

	def testEventManagerAddChannel(self):
		"""Test EventManager.addChannel

		1. Test that a channel can be added
		2. Test that the channl was actually added
		3. Test the returned channel id against getChannelID()
		"""

		#1
		channel = self.event.addChannel("foobar")

		#2
		self.assertTrue(
				self.event.getChannelID("foobar") is not None)

		#3
		self.assertEquals(channel,
				self.event.getChannelID("foobar"))

	def testEventManagerGetChannelID(self):
		"""Test EventManager.getChannelID

		1. Test that a channel's id that was added is not None
		2. Test test a channel's id that was added is of type
		   int
		3. Test that a bogus channel's id is None
		"""

		channel = self.event.addChannel("foobar")

		#1
		self.assertTrue(
				self.event.getChannelID("foobar") is not None)
		self.assertEquals(channel,
				self.event.getChannelID("foobar"))

		#2
		self.assertEquals(
				type(self.event.getChannelID("foobar")),
				int)

		#3
		self.assertTrue(
				self.event.getChannelID("asdf") is None)
	
	def testEventManagerRemoveChannel(self):
		"""Test EventManager.removeChannel

		1. Test that a channel can be removed.
		2. Test that that channel's id is now None
		"""

		#1
		self.event.removeChannel("foobar")

		#2
		self.assertTrue(
				self.event.getChannelID("foobar") is None)

	def testEventManagerAddRemove(self):
		"""Test EventManager.add & EventManager.remove

		1. Test that filters/listeners can be added to the
		   global channel
		2. Test that filters/listeners can be added to a
		   specific channel
		3. Test that a channel can be given as a string
		   identifying that channel by name vs. id
		4. Test that non-filters/listeners cannot be added
		   and raises an EventError
		5. Test that filters/listeners added to a non-existent
		   channel raise an EventError
		6. Test that filters/listeners are added to the right
		   container and right channel
		7. Test that filters/listeners can be removed from
		   all channels
		8. Test that filters/listeners can be removed from
		   a specific channel
		"""

		@filter("FOO")
		def onFOO():
			pass

		@listener("BAR")
		def onBAR():
			pass

		def onTEST():
			pass

		#1
		self.event.add(onFOO)
		self.event.add(onBAR)

		channel = self.event.addChannel("test")

		#2
		self.event.add(onFOO, channel) 
		#3
		self.event.add(onBAR, "test")

		#4
		try:
			self.event.add(onTEST)
			self.assertFalse(False)
		except EventError:
			self.assertTrue(True)

		#5
		try:
			self.event.add(onFOO, 1234)
			self.assertFalse(False)
		except EventError:
			self.assertTrue(True)

		#6
		self.assertTrue(
				onFOO in self.event._filters[
					self.event.getChannelID("global")])
		self.assertTrue(
				onBAR in self.event._listeners[
					self.event.getChannelID("test")])
		self.assertTrue(
				onFOO in self.event._filters[
					self.event.getChannelID("global")])
		self.assertTrue(
				onBAR in self.event._listeners[
					self.event.getChannelID("test")])

		#7
		self.event.remove(onFOO)
		self.assertTrue(
				onFOO not in self.event._filters.values()[0] and
				onFOO not in self.event._listeners.values()[0])

		#8
		self.event.remove(onBAR, self.event.getChannelID("test"))
		self.assertTrue(
				onBAR in self.event._listeners[
					self.event.getChannelID("global")] and
				onBAR not in self.event._listeners[
					self.event.getChannelID("test")])

		self.event.remove(onBAR)
		self.event.removeChannel("test")
	
	def testEventManagerPushFlushSend(self):
		"""Test EventManager's push, flush and send

		Test also the synonyms:
		 * pushEvent
		 * flushEvents
		 * sendEvent

		1. Test that push is a synonym of pushEvent
		2. Test that flush is a synonym of flushEvents
		3. Test that the event queue is empty after flushing
		4. Test that send is a synonym of sendEvent
		5. Test that events cannot be sent to the global
		   channel
		6. Test that a channel can be given as a string
		   identifying that channel by name vs. id
		7. Test that _channel and _time are set on
		   the event
		8 Test that a filter actually can stop further event
		   processing
		"""

		import time

		self.flag = False

		@filter()
		def onCHECK(event, test, time):
			#7
			test.assertTrue(
					hasattr(event, "_time") and
					type(event._time) == float and
					int(event._time) == int(time))
			test.assertTrue(
					hasattr(event, "_channel") and
					type(event._channel) == int)
			return False, event

		@listener("test")
		def onTEST(test, time):
			test.flag = True

		@filter()
		def onSTOP(event, test, time, stop=False):
			return stop, event

		channel = self.event.addChannel("test")
		self.event.add(onSTOP)
		self.event.add(onCHECK)
		self.event.add(onTEST, channel)

		#1 & #2
		self.event.push(Event(self, time.time()), channel)
		self.event.flush()
		self.assertTrue(self.flag == True)
		self.flag = False
		self.event.pushEvent(Event(self, time.time()), channel)
		self.event.flushEvents()
		self.assertTrue(self.flag == True)
		self.flag = False

		#3
		self.assertTrue(self.event._queue == [])

		#4
		self.event.send(Event(self, time.time()), channel)
		self.assertTrue(self.flag == True)
		self.flag = False
		self.event.sendEvent(Event(self, time.time()), channel)
		self.assertTrue(self.flag == True)
		self.flag = False

		#5
		try:
			self.event.send(
					Event(), self.event.getChannelID("global"))
			self.assertFalse(False)
		except EventError:
			self.assertTrue(True)

		#6
		self.event.send(Event(self, time.time()), channel)
		self.assertTrue(self.flag == True)
		self.flag = False

		#8
		self.event.send(Event(self, time.time(), stop=True),
				channel)
		self.assertTrue(self.flag == False)

def suite():
	return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
	unittest.main()
