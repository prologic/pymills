#!/usr/bin/env python

import optparse

import pymills
from pymills.event import listener, Component, Event, Manager, Bridge

USAGE = "%prog [options]"
VERSION = "%prog v" + pymills.__version__

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

	return opts, args

class Adder(Component):

	@listener("add")
	def onADD(self, x, y):
		print "Adding %s + %s" % (x, y)
		r = x + y
		self.push(Event(r), "result")

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 8000

	e = Manager()
	bridge = Bridge(e, port=port, address=address)
	Adder(e)

	while True:
		try:
			e.flush()
			bridge.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
