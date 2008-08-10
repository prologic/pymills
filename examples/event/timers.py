#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills import event
from pymills.event import *
from pymills.event.timers import Timers

class HelloWorld(Component):

	@listener("timer:hello")
	def onHELLO(self):
		print "Hello World"

	@listener("timer:foo")
	def onFOO(self):
		print "Foo"

	@listener("timer:bar")
	def onBAR(self):
		print "Bar"

def main():
	event.manager += HelloWorld()

	timers = Timers()
	event.manager += timers


	timers.add(5, Event("Hello"), "hello")
	timers.add(1, Event("Foo"), "foo", persist=True)
	timers.add(3, Event("Bar"), "bar", persist=True, start=True)

	while True:
		try:
			manager.flush()
			timers.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
