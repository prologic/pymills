#!/usr/bin/env python

from pymills.timers import Timers
from pymills.event import Component, EventManager, \
		filter, listener

class HelloWorld(Component):

	@filter()
	def onDEBUG(self, event):
		print event
		return False, event

	@listener("timer")
	def onHELLO(self, name, length, channel):
		print "Hello World"

	@listener("foo")
	def onFOO(self, name, length, channel):
		print "foo"
	
	@listener("bar")
	def onBAR(self, name, length, channel, **kwargs):
		print "bar:", kwargs
	
def main():
	event = EventManager()
	timers = Timers(event)
	helloWorld = HelloWorld(event)

	timers.add("hello", 5)
	timers.add("foo", 2, "foo", True)
	timers.add("bar", 3, "bar", foo="bar")

	while True:
		timers.process()
		event.flush()

if __name__ == "__main__":
	main()
