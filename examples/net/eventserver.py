#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, filter, Component, \
		Event, Remote

class HelloWorld(Component):

	@filter()
	def onDEBUG(self, event):
		print "DEBUG: %s (From: %s)" % (event, event._source)

	@listener("hello")
	def onHELLO(self, event, message=""):
		print message
		self.push(Event(message), "received")

def main():
	e = Remote()
	helloWorld = HelloWorld(e)

	while True:
		try:
			e.flush()
			e.process()
		except KeyboardInterrupt:
			break
	e.flush()

if __name__ == "__main__":
	main()
