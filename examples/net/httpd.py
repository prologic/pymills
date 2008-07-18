#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import time
import math
import hotshot
import optparse
import hotshot.stats

import pymills
from pymills.net.sockets import TCPServer
from pymills import __version__ as systemVersion
from pymills.net.http import HTTP, ResponseEvent, Response
from pymills.event import listener, UnhandledEvent, Component, Manager

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
	parser.add_option("-p", "--profile",
			action="store_true", default=False, dest="profile",
			help="Enable execution profiling support")

	opts, args = parser.parse_args()

	return opts, args

class WebServer(TCPServer, HTTP):

	@listener("get")
	def onGET(self, req):
		res = Response(req, "OK")
		self.push(ResponseEvent(res), "response")

class Stats(Component):

	def __init__(self, *args, **kwargs):
		super(Stats, self).__init__(*args, **kwargs)

		self.reqs = 0

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
	stats = Stats(e)

	while True:
		try:
			e.flush()
			server.process()
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break
	e.flush()

	eTime = time.time()

	tTime = eTime - sTime

	print "Total Requests: %d" % stats.reqs
	print "%d/s after %0.2fs" % (
			int(math.ceil(float(stats.reqs) / tTime)),
			tTime)

	if opts.profile:
		profiler.stop()
		profiler.close()

		stats = hotshot.stats.load("httpd.prof")
		stats.strip_dirs()
		stats.sort_stats("time", "calls")
		stats.print_stats(20)

if __name__ == "__main__":
	main()
