#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import readline
import optparse

from pymills.net.sockets import TCPClient
from pymills import __version__ as systemVersion
from pymills.event import listener, Manager, UnhandledEvent

class TelnetClient(TCPClient):

	@listener("connect")
	def onCONNECT(self, host, port):
		print "Connected to %s" % host

	@listener("read")
	def onREAD(self, line):
		print line

USAGE = "%prog [options] <host> [<port>]>"
VERSION = "%prog v" + systemVersion

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-s", "--ssl",
			action="store_true", default=False, dest="ssl",
			help="Enable Secure Socket Layer (SSL)")

	opts, args = parser.parse_args()

	if len(args) < 1:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

def main():
	opts, args = parse_options()

	host = args[0]
	if len(args) > 1:
		port = int(args[1])
	else:
		port = 23

	e = Manager()
	client = TelnetClient(e)

	print "Trying %s..." % host
	client.open(host, port, ssl=opts.ssl)

	while True:
		try:
			e.flush()
			client.poll()
			line = raw_input().strip()
			client.write("%s\n" % line)
		except KeyboardInterrupt:
			break
	client.close()
	try:
		e.flush()
	except UnhandledEvent:
		pass

if __name__ == "__main__":
	main()
