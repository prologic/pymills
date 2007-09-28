#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.timers import Timers
from pymills.event import Component, Manager, \
		filter, listener

class HelloWorld(Component):

	@filter()
	def onDEBUG(self, event):
		print event

	@listener("timer")
	def onHELLO(self, n):
		print "Hello World"

	@listener("foo")
	def onFOO(self, n):
		print "foo"

	@listener("bar")
	def onBAR(self, n, **kwargs):
		print "bar:", kwargs

def main():
	e = Manager()
	timers = Timers(e)
	helloWorld = HelloWorld(e)

	timers.add(5, "hello")
	timers.add(2, "foo", forever=True)
	timers.add(3, "bar", foo="bar")

	while True:
		timers.process()
		e.flush()

if __name__ == "__main__":
	main()
