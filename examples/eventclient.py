#!/usr/bin/env python

import time

from pymills.event import *

class Foo(Component):

	@listener("foo")
	def onFOO(self, event):
		print event

def main():

	nodes = ["10.0.0.2"]

	event = RemoteManager(nodes)
	foo = Foo(event)

	hello = Event(message="Hello World")

	sTime = time.time()

	while True:

		if (time.time() - sTime) > 5:
			print "Sending event..."
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
