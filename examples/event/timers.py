#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

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
	HelloWorld(e)
	timers = Timers(e)

	timers.add(5, Event("Hello"), "hello")
	timers.add(1, Event("Foo"), "foo", persist=True)
	timers.add(3, Event("Bar"), "bar", persist=True, start=True)

	while True:
		try:
			e.flush()
			timers.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
