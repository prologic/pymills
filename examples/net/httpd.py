#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import os
import time
import math
import hotshot
import optparse
import hotshot.stats
from traceback import format_exc

from pymills.event import *
from pymills.net.sockets import TCPServer
from pymills.net.http import HTTP, Response
from pymills import __version__ as systemVersion

USAGE = "%prog [options] [content]"
VERSION = "%prog v" + systemVersion

ERRORS = [
		(0, "Invalid requests spcified. Must be an integer."),
		(1, "Invalid time spcified. Must be an integer."),
		]

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
	parser.add_option("-t", "--time",
			action="store", default=0, dest="time",
			help="Stop after specified elapsed seconds")
	parser.add_option("-r", "--reqs",
			action="store", default=0, dest="reqs",
			help="Stop after specified number of requests")
	parser.add_option("-p", "--profile",
			action="store_true", default=False, dest="profile",
			help="Enable execution profiling support")
	parser.add_option("-d", "--debug",
			action="store_true", default=False, dest="debug",
			help="Enable debug mode. (Default: False)")

	opts, args = parser.parse_args()

	try:
		opts.reqs = int(opts.reqs)
	except Exception, e:
		print str(e)
		parser.exit(ERRORS[0][0], ERRORS[0][1])

	try:
		opts.time = int(opts.time)
	except Exception, e:
		print str(e)
		parser.exit(ERRORS[1][0], ERRORS[1][1])

	return opts, args

###
### Components
###

class Test(Component):

	content = "OK"

	@listener("get")
	def onGET(self, req):
		res = req.res
		if os.path.exists(self.content):
			res.body = open(self.content, "rb")
		else:
			res.body = self.content
		self.push(Response(res), "response")

class WebServer(TCPServer, HTTP): pass

class Stats(Component):

	reqs = 0
	events = 0

	@filter()
	def onEVENTS(self, *args, **kwargs):
		self.events += 1

	@listener("get")
	def onREQUESTS(self, *args, **kwargs):
		self.reqs += 1

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

	sTime = time.time()

	if opts.profile:
		profiler = hotshot.Profile("httpd.prof")
		profiler.start()

	debugger.set(opts.debug)
	debugger.IgnoreEvents = ["Read", "Write", "Close"]

	server = WebServer(e, port, address)
	test = Test(e)
	stats = Stats(e)

	if args:
		test.content = args[0]

	while True:
		try:
			e.flush()
			server.poll()

			if opts.reqs > 0 and stats.reqs > opts.reqs:
				break
			if opts.time > 0 and (time.time() - sTime) > opts.time:
				break
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break

	eTime = time.time()
	tTime = eTime - sTime

	print "Total Requests: %d (%d/s after %0.2fs)" % (
			stats.reqs, int(math.ceil(float(stats.reqs) / tTime)), tTime)
	print "Total Events:   %d (%d/s after %0.2fs)" % (
			stats.events, int(math.ceil(float(stats.events) / tTime)), tTime)

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
