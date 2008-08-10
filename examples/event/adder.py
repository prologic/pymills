#!/usr/bin/env python

import optparse

import pymills
from pymills import event
from pymills.event import *

USAGE = "%prog [options]"
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

class Result(Event): pass

###
### Components
###

class Adder(Component):

	@listener("newinput")
	def onNEWINPUT(self, s):
		print "Evaluating: %s" % s
		r = eval(s)
		self.push(Result(r), "result")

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

	debugger.set(opts.debug)
	debugger.IgnoreEvents.extend(["Read", "Write"])
	
	bridge = Bridge(port, address=address)
	event.manager += bridge
	event.manager += Adder()

	while True:
		try:
			manager.flush()
			bridge.poll()
		except KeyboardInterrupt:
			break

###
### Entry Point
###

if __name__ == "__main__":
	main()
