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

class Server(TCPServer):

	channel = "server"

	def __init__(self, *args, **kwargs):
		super(Server, self).__init__(*args, **kwargs)

		self.targets = [x.split(":") for x in kwargs.get("targets", [])]
		self.clients = []
		self.sockMap = {}
		self.n = 0

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		host, port = self.targets[self.n]
		port = int(port)

		hash = md5.new("%s:%s" % (host, port)).hexdigest()

		client = Client(self.manager, server=self, sock=sock, channel=id(sock))
		client.open(host, port)

		self.clients.append(client)
		self.sockMap[sock] = client

		self.n += 1
		if self.n == len(self.targets):
			self.n = 0

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		client = self.sockMap[sock]
		client.close()
		client.unregister()
		self.clients.remove(client)
		del self.sockMap[sock]
		del client

	@listener("read")
	def onREAD(self, sock, data):
		client = self.sockMap[sock]
		client.write(data)
	
class Client(TCPClient):

	def __init__(self, *args, **kwargs):
		super(Client, self).__init__(*args, **kwargs)

		self.server = kwargs["server"]
		self.sock = kwargs["sock"]

	@listener("disconnect")
	def onDISCONNECT(self):
		if self in self.server.clients:
			self.server.close(self.sock)

	@listener("read")
	def onREAD(self, data):
		self.server.write(self.sock, data)

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
	def onDEBUG(self, event, *args, **kwargs):
		self.events += 1

	@listener("server:connect")
	def onGET(self, *args, **kwargs):
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
		profiler = hotshot.Profile(".tcpbalancer.prof")
		profiler.start()

	e = Manager()
	server = Server(e, port, address, targets=args)
	stats = Stats(e)

	while True:
		try:
			e.flush()
			server.poll()
			[(e.flush(), client.poll()) for client in server.clients]

			if opts.reqs > 0 and stats.reqs > opts.reqs:
				e.send(Event(), "stop")
				break
			if opts.time > 0 and (time.time() - sTime) > opts.time:
				e.send(Event(), "stop")
				break

		except UnhandledEvent, event:
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

		stats = hotshot.stats.load(".tcpbalancer.prof")
		stats.strip_dirs()
		stats.sort_stats("time", "calls")
		stats.print_stats(20)

if __name__ == "__main__":
	main()
