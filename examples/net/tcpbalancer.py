#!/usr/bin/env python

import md5
import hotshot
import optparse
import hotshot.stats

from pymills import __version__ as systemVersion
from pymills.net.sockets import TCPServer, TCPClient
from pymills.event import filter, listener, Manager, UnhandledEvent, Event

USAGE = "%prog [options] <host1:port1> <host2:port2> [<hostN:portN>]"
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

	if not args:
		parser.print_help()
		raise SystemExit, 1
	
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

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 80

	if opts.profile:
		profiler = hotshot.Profile(".tcpbalancer.prof")
		profiler.start()

	e = Manager()
	server = Server(e, port, address, targets=args)

	while True:
		try:
			e.flush()
			server.process()
			[(e.flush(), client.process()) for client in server.clients]
		except UnhandledEvent, event:
			pass
		except KeyboardInterrupt:
			break
	e.flush()

	if opts.profile:
		profiler.stop()
		profiler.close()

		stats = hotshot.stats.load(".tcpbalancer.prof")
		stats.strip_dirs()
		stats.sort_stats("time", "calls")
		stats.print_stats(20)

if __name__ == "__main__":
	main()