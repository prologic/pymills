#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import hotshot
import optparse
import hotshot.stats

from pymills import event
from pymills.event import *
from pymills.net.sockets import TCPServer
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
	parser.add_option("-p", "--profile",
			action="store_true", default=False, dest="profile",
			help="Enable execution profiling support")
	parser.add_option("-d", "--debug",
			action="store_true", default=False, dest="debug",
			help="Enable debug mode. (Default: False)")

	opts, args = parser.parse_args()

	return opts, args

###
### Components
###

class Test(Component):

	@listener("hello")
	def onHello(self, request, response):
		response.body = "Hello World!"
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

	if opts.profile:
		profiler = hotshot.Profile("httpd.prof")
		profiler.start()

	if opts.debug:
		debugger.enable()
		debugger.IgnoreEvents = ["Read", "Write", "Close"]
		event.manager += debugger

	server = WebServer(port, address)
	dispatcher = Dispatcher()
	if args:
		dispatcher.docroot = args[0]

	event.manager += server
	event.manager += Test()
	event.manager += dispatcher

	while True:
		try:
			manager.flush()
			server.poll()
		except KeyboardInterrupt:
			break

	if opts.profile:
		profiler.stop()
		profiler.close()

		stats = hotshot.stats.load("httpd.prof")
		stats.strip_dirs()
		stats.sort_stats("time", "calls")
		stats.print_stats(20)

###
### Entry Point
###

if __name__ == "__main__":
	main()
