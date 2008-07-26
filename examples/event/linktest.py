#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep

from pymills.event import listener, Component, Event, Manager

class Foo(Component):

	@listener("foo")
	def onFOO(self):
		print "Foo",
		self.send(Event("Bar"), "bar")

class Bar(Component):

	@listener("bar")
	def onBAR(self):
		print "Bar!"

def main():
	e = Manager()
	Foo(e).link(Bar(e))

	while True:
		try:
			e.flush()
			e.push(Event("Foo"), "foo")
			sleep(1)
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
