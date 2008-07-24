#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import optparse

import pymills
from pymills.event import listener, Component, Event, Manager, Bridge

USAGE = "%prog [options] <host> <port>"
VERSION = "%prog v" + pymills.__version__

class Calc(Component):

	@listener("result")
	def onRESULT(self, r):
		print "Result: %s" % r

def parse_options():
	"""parse_options() -> opts, args

	Parse the command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-b", "--bind",
			action="store", default="0.0.0.0:8000", dest="bind",
			help="Bind to address:port")

	opts, args = parser.parse_args()

	if len(args) < 2:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 8000

	nodes = [(args[0], int(args[1]))]

	e = Manager()
	bridge = Bridge(e, port=port, address=address, nodes=nodes)
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
