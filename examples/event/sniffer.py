#!/usr/bin/env python

import optparse

import pymills
from pymills.event import Manager, Bridge, Debugger, Read, Write

USAGE = "%prog [options] [host[:port]]"
VERSION = "%prog v" + pymills.__version__

def parse_options():
	"""parse_options() -> opts, args

	Parse the command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-b", "--bind",
			action="store", default="0.0.0.0:9000", dest="bind",
			help="Bind to address:port")

	opts, args = parser.parse_args()

	return opts, args

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 9000

	if args:
		x = args[0].split(":")
		if len(x) > 1:
			nodes = [(x[0], int(x[1]))]
		else:
			nodes = [(x[0], 8000)]
	else:
		nodes = []

	e = Manager()
	bridge = Bridge(e, port=port, address=address, nodes=nodes)
	debugger = Debugger(e)
	debugger.IgnoreEvents.extend(["Read", "Write"])

	while True:
		try:
			e.flush()
			bridge.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
