#!/usr/bin/env python

import threading
from time import sleep

from pymills.event import listener, filter, Component, \
		Event, EventManager

class Foo(Component):

	@listener("foo")
	def onFOO(self, event):
		self.send(Event(), "bar")
	
class Bar(Component):

	@listener("bar")
	def onBAR(self, event):
		print "FooBar!"

def main():
	event = EventManager()
	foo = Foo(event)
	bar = Bar(event)

	foo.link(bar)

	while True:
		try:
			event.flush()
			event.push(Event("foo"), "foo")
			sleep(1)
		except KeyboardInterrupt:
			break

	event.flush()

if __name__ == "__main__":
	main()
