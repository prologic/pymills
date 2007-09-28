#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, Component, Event, \
		Manager

class Foo(Component):

	__channelPrefix__ = "foo"

	@listener("test")
	def onTEST(self, event, s):
		print "Hello %s" % s

class Bar(Component):

	__channelPrefix__ = "bar"

	@listener("test")
	def onTEST(self, event, s):
		print "Hello %s" % s

def main():
	event = Manager()

	foo = Foo(event)
	bar = Bar(event)

	event.send(Event("hello from Foo"), "test", foo)
	event.send(Event("hello from Bar"), "test", bar)

if __name__ == "__main__":
	main()
