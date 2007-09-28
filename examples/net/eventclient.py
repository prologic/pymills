#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import time

from pymills.event import listener, filter, Component, \
		Event, RemoteManager

class Foo(Component):

	@filter()
	def onDEBUG(self, event):
		print "DEBUG: %s" % event

	@listener("received")
	def onRECEIVED(self, event, message=""):
		print "%s received" % message

def main():

	nodes = (
			"202.63.43.98",
			)

	e = RemoteManager(nodes)
	foo = Foo(e)

	sTime = time.time()

	while True:
		try:
			e.flush()
			e.process()
			if (time.time() - sTime) > 5:
				e.push(Event(message="hello"), "hello")
				sTime = time.time()
		except KeyboardInterrupt:
			break

	e.flush()

if __name__ == "__main__":
	main()
