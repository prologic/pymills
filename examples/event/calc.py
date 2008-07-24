#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, Component, Event, Manager, Bridge

class Calc(Component):

	@listener("result")
	def onRESULT(self, r):
		print "Result: %s" % r

def main():

	nodes = [("localhost", 9000)]

	e = Manager()
	bridge = Bridge(e, port=9001, nodes=nodes)
	Calc(e)

	x = float(raw_input("x: "))
	y = float(raw_input("y: "))

	e.push(Event(x, y), "add")

	while True:
		try:
			e.flush()
			bridge.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
