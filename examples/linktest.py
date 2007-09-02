#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep

from pymills.event import listener, Component, \
		Event, Manager

class Foo(Component):

	@listener("foo")
	def onFOO(self, event):
		self.send(Event(), "bar")

class Bar(Component):

	@listener("bar")
	def onBAR(self, event):
		print "FooBar!"

def main():
	event = Manager()
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
