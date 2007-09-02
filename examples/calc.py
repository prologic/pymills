#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, Component, \
		Event, Remote

class Calc(Component):

	@listener("result")
	def onRESULT(self, r):
		print "Result: %s" % r

def main():

	nodes = ("daisy:12000",)

	event = Remote(nodes)
	calc = Calc(event)

	x = float(raw_input("x: "))
	y = float(raw_input("y: "))

	event.push(Event(x, y), "add")

	while True:
		try:
			event.flush()
			event.process()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
