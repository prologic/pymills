#!/usr/bin/env python

import time

from pymills.event import listener, filter, Component, \
		Event, RemoteManager

class Foo(Component):

	@filter()
	def onDEBUG(self, event):
		print event
		return False, event

	@listener("received")
	def onRECEIVED(self, event, message=""):
		print "%s received" % message

def main():

	nodes = (
			"202.63.43.98",
			)

	event = RemoteManager(nodes)
	foo = Foo(event)

	hello = Event(message="Hello World")

	sTime = time.time()

	while True:

		if (time.time() - sTime) > 5:
			event.push(hello, "hello")
			sTime = time.time()

		try:
			event.flush()
			event.process()
		except KeyboardInterrupt:
			break
	event.flush()

if __name__ == "__main__":
	main()
