#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, filter, Component, \
		Event, RemoteManager

class HelloWorld(Component):

	@filter()
	def onDEBUG(self, event):
		print "DEBUG: %s (From: %s)" % (event, event._source)
		return False, event

	@listener("hello")
	def onHELLO(self, event, message=""):
		print message
		self.event.push(Event(message), "received")

def main():
	event = RemoteManager()
	helloWorld = HelloWorld(event)

	while True:
		try:
			event.flush()
			event.process()
		except KeyboardInterrupt:
			break
	event.flush()

if __name__ == "__main__":
	main()
