#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import sys
import optparse

import pymills
from pymills import event
from pymills.event import *
from pymills.io import Stdin

USAGE = "%prog [options] [host[:port]]"
VERSION = "%prog v" + pymills.__version__

###
### Functions
###

def parse_options():
	"""parse_options() -> opts, args

	Parse the command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-b", "--bind",
			action="store", default="0.0.0.0:8000", dest="bind",
			help="Bind to address:port")
	parser.add_option("-d", "--debug",
			action="store_true", default=False, dest="debug",
			help="Enable debug mode. (Default: False)")

	opts, args = parser.parse_args()

	return opts, args

###
### Events
###

class NewInput(Event): pass

###
### Components
###

class Input(Stdin):

	@listener("read")
	def onREAD(self, data):
		self.push(NewInput(data.strip()), "newinput")

class Calc(Component):

	@listener("result")
	def onRESULT(self, r):
		sys.stdout.write("%s\n" % r)
		sys.stdout.write(">>> ")
		sys.stdout.flush()

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 8000

	if args:
		x = args[0].split(":")
		if len(x) > 1:
			nodes = [(x[0], int(x[1]))]
		else:
			nodes = [(x[0], 8000)]
	else:
		nodes = []

	input = Input()
	event.manager += input

	event.manager += Calc()

	debugger.set(opts.debug)
	debugger.IgnoreEvents.extend(["Read", "Write"])
	event.manager += debugger

	bridge = Bridge(port, address=address, nodes=nodes)
	event.manager += bridge

	sys.stdout.write(">>> ")
	sys.stdout.flush()

	while True:
		try:
			manager.flush()
			input.poll()
			bridge.poll()
		except KeyboardInterrupt:
			break

###
### Entry Point
###

if __name__ == "__main__":
	main()
