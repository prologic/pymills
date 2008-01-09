#!/usr/bin/env python

import optparse

from pymills import __version__ as systemVersion
from pymills.net.sockets import TCPServer, TCPClient
from pymills.event import listener, Manager, UnhandledEvent, Event

USAGE = "%prog [options]"
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
	parser.add_option("-p", "--port",
			action="store", default=None, dest="port",
			help="Port to listen on (Required)")
	parser.add_option("-c", "--connect",
			action="store", default=None, dest="connect",
			help="hostname:port to connect to (Required)")

	opts, args = parser.parse_args()

	if opts.port is None:
		parser.print_help()
		raise SystemExit, 1
	
	if opts.connect is None:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

class NewConnection(Event):

	def __init__(self, host, port):
		super(NewConnection, self).__init__(host, port)

class CloseConnection(Event):
	pass

class Data(Event):

	def __init__(self, data):
		super(Data, self).__init__(data)

class Server(TCPServer):

	__channelPrefix__ = "server"

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		print "[Server]: New Connection: %s:%s" % (host, port)
		self.push(NewConnection(host, port), "client:newconnection")

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		print "[Server]: Disconnection: %s" % sock
		self.push(CloseConnection(), "client:closeconnection")

	@listener("read")
	def onREAD(self, sock, data):
		data = data.strip()
		print "[Server]: (IN) %s" % data
		self.push(Data(data), "client:dataout")
	
	@listener("error")
	def onERROR(self, sock, error):
		print "[Server]: ERROR: (%s) %s" % (sock, error)
	
	@listener("datain")
	def onDATAIN(self, data):
		print "[Server]: (OUT) %s" % data
		self.broadcast(data)

class Client(TCPClient):

	__channelPrefix__ = "client"

	def __init__(self, event, host, port):
		super(Client, self).__init__(event)

		self.host = host
		self.port = port

	@listener("newconnection")
	def onNEWCONNECTION(self, host, port):
		print "[Client]: Connecting to: %s:%s" % (self.host, self.port)
		self.open(self.host, self.port)
	
	@listener("closeconnection")
	def onCLOSECONNECTION(self):
		print "[Client]: Closing connection..."
		self.close()
	
	@listener("dataout")
	def onDATAOUT(self, data):
		print "[Client]: (OUT) %s" % data
		self.write("%s\n" % data)

	@listener("connect")
	def onCONNECT(self, host, port):
		print "[Client]: Connected to %s" % host

	@listener("disconnect")
	def onDISCONNECT(self):
		print "[Client]: Disconnected"

	@listener("error")
	def onERROR(self, error):
		print "[Client]: ERROR: %s" % error

	@listener("read")
	def onREAD(self, data):
		print "[Client]: (IN) %s" % data
		self.push(Data(data), "server:datain")

def main():
	opts, args = parse_options()

	serverPort = int(opts.port)
	x, y = opts.connect.split(":")
	clientHost = x
	clientPort = int(y)

	e = Manager()
	server = Server(e, serverPort)
	client = Client(e, clientHost, clientPort)

	while True:
		try:
			server.process()
			if client.connected:
				client.process()
			e.flush()
		except KeyboardInterrupt:
			break
	e.flush()

if __name__ == "__main__":
	main()
