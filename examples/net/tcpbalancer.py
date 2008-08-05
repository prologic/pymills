#!/usr/bin/env python

import md5
import math
import time
import hotshot
import optparse
import hotshot.stats

from pymills.event import UnhandledEvent, Event
from pymills import __version__ as systemVersion
from pymills.net.sockets import TCPServer, TCPClient
from pymills.event import filter, listener, Manager, Component

USAGE = "%prog [options] <host1:port1> <host2:port2> [<hostN:portN>]"
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

	opts, args = parser.parse_args()

	if not args:
		parser.print_help()
		raise SystemExit, 1

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
### Events
###

class Query(Event): pass
class Busy(Event): pass
class Ready(Event): pass
class ClientOpen(Event): pass
class ClientData(Event): pass
class ClientClosed(Event): pass
class TargetData(Event): pass
class TargetClosed(Event): pass

###
### Components
###

class Balancer(Component):

	targets = []

class Server(TCPServer):

	channel = "server"
	client = None

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		self.push(ClientOpen(), "target:open")

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		self.client = None
		self.push(ClientClosed(), "target:closed")

	@listener("read")
	def onREAD(self, sock, data):
		self.push(ClientData(data), "target:data")

	@listener("closed")
	def onCLOSED(self):
		if self.client:
			self.close(self.client)

	@listener("data")
	def onDATA(self, data):
		self.write(self.client, data)

class Target(TCPClient):

	channel = "target"

	connect = None

	@listener("open")
	def onOPEN(self):
		self.open(*self.connect)
	
	@listener("data")
	def onDATA(self, data):
		self.write(data)

	@listener("closed")
	def onCLOSED(self):
		self.close()

	@listener("read")
	def onREAD(self, data):
		self.push(TargetData(data), "server:data")

	@listener("disconnect")
	def onDISCONNECT(self):
		self.push(TargetClosed(), "server:closed")

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
		bind = (address, port)
	else:
		bind = (opts.bind, 8000)

	if ":" in args[0]:
		address, port = args[0].split(":")
		port = int(port)
		connect = (address, port)
	else:
		connect = (args[0], 8000)

	debugger.set(opts.debug)

	server = Server(e, address=bind[0], port=bind[1])
	target = Target(e)

	server.target = target
	target.connect = connect

	while True:
		try:
			e.flush()
			server.poll()
			if target.connected:
				target.poll()
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			target.close()
			server.close()
			break

###
### Entry Point
###

if __name__ == "__main__":
	main()
class State(Component):

	done = False

	@listener("stop")
	def onSTOP(self):
		self.done = True

class Stats(Component):

	def __init__(self, *args, **kwargs):
		super(Stats, self).__init__(*args, **kwargs)

		self.reqs = 0
		self.events = 0

	@filter()
	def onDEBUG(self, *args, **kwargs):
		self.events += 1

	@listener("server:connect")
	def onGET(self, *args, **kwargs):
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
		address, port = opts.bind, 8000

	connections = []
	for arg in args:
		if ":" in args[0]:
			address, port = arg.split(":")
			port = int(port)
		else:
			address = arg
			port = 8000
		connections.append((address, port))

	sTime = time.time()

	if opts.profile:
		profiler = hotshot.Profile(".tcpbalancer.prof")
		profiler.start()

	debugger.set(opts.debug)

	stats = Stats(e)

	server = Server(e, address=bind[0], port=bind[1])

	targets = []
	for i, connect in enumerate(connections):
		target = Target(e, channel="target:%d" % i)
		target.connect = connect

	while True:
		try:
			e.flush()
			server.poll()
			[target.poll() for target in targets if target.connected]

			if opts.reqs > 0 and stats.reqs > opts.reqs:
				e.send(Event(), "stop")
				break
			if opts.time > 0 and (time.time() - sTime) > opts.time:
				e.send(Event(), "stop")
				break

		except UnhandledEvent, event:
			pass
		except KeyboardInterrupt:
			server.close()
			[target.close() for target in targets if target.connected]
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

		stats = hotshot.stats.load(".tcpbalancer.prof")
		stats.strip_dirs()
		stats.sort_stats("time", "calls")
		stats.print_stats(20)

###
### Entry Point
###

if __name__ == "__main__":
	main()
