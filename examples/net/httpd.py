#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import optparse

import pymills
from pymills.net.http import HTTP
from pymills.net.sockets import TCPServer
from pymills import __version__ as systemVersion
from pymills.event import listener, UnhandledEvent, Manager

#pymills.net.sockets.POLL_INTERVAL = 0

USAGE = "%prog [options]"
VERSION = "%prog v" + systemVersion

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-b", "--bind",
			action="store", default="0.0.0.0:8000", dest="bind",
			help="Bind to address:port")

	opts, args = parser.parse_args()

	return opts, args

class WebServer(TCPServer, HTTP):

	@listener("get")
	def onGET(self, req):
		return "OK"

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 80

	e = Manager()
	server = WebServer(e, port, address)

	while True:
		try:
			e.flush()
			server.process()
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break
	e.flush()

if __name__ == "__main__":
	main()
