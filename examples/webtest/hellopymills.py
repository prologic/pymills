#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import optparse

from pymills import event
from pymills.event import manager
from pymills.net.sockets import TCPServer
from pymills.event.core import listener, Component
from pymills.net.http import HTTP, Response, Dispatcher
from pymills import __version__ as systemVersion

USAGE = "%prog [options] [path]"
VERSION = "%prog v" + systemVersion

###
### Functions
###

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

###
### Components
###

class Test(Component):

	channel = "/"

	@listener("index")
	def onINDEX(self, request, response):
		self.send(Response(response), "response")

	@listener("hello")
	def onHello(self, request, response):

		if request.cookie.get("seen", False):
			response.body = "Seen you before!"
		else:
			response.body = "Hello World!"
			response.cookie["seen"] = True

		self.send(Response(response), "response")

	@listener("test")
	def onTEST(self, request, response):
		response.body = "OK"
		self.send(Response(response), "response")

class WebServer(TCPServer, HTTP): pass

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 80

	server = WebServer(port, address)
	dispatcher = Dispatcher()

	event.manager += server
	event.manager += Test()
	event.manager += dispatcher

	while True:
		try:
			manager.flush()
			server.poll()
		except KeyboardInterrupt:
			break

###
### Entry Point
###

if __name__ == "__main__":
	main()
