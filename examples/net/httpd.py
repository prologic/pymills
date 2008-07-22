#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import time
import math
import hotshot
import optparse
import hotshot.stats
from traceback import format_exc

import pymills
from pymills.event import Event
from pymills.net.sockets import TCPServer
from pymills import __version__ as systemVersion
from pymills.net.http import HTTP, ResponseEvent, Response
from pymills.event import filter, listener, UnhandledEvent, Component, Manager

USAGE = "%prog [options]"
VERSION = "%prog v" + systemVersion

ERRORS = [
		(0, "Invalid requests spcified. Must be an integer."),
		(1, "Invalid time spcified. Must be an integer."),
		]

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

class Test(Component):

	@listener("get")
	def onGET(self, req):
		res = Response(req)
		res.write("OK")
		self.push(ResponseEvent(res), "response")

class WebServer(TCPServer, HTTP):
	pass

class Stats(Component):

	def __init__(self, *args, **kwargs):
		super(Stats, self).__init__(*args, **kwargs)

		self.reqs = 0
		self.events = 0

	@filter()
	def onDEBUG(self, event, *args, **kwargs):
		self.events += 1

	@listener("get")
	def onGET(self, req):
		self.reqs += 1

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

	e = Manager()
	server = WebServer(e, port, address)
	test = Test(e)
	stats = Stats(e)

	while True:
		try:
			e.flush()
			server.poll()

			if opts.reqs > 0 and stats.reqs > opts.reqs:
				e.send(Event(), "stop")
				break
			if opts.time > 0 and (time.time() - sTime) > opts.time:
				e.send(Event(), "stop")
				break

		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break
	e.flush()
	print

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

if __name__ == "__main__":
	main()
