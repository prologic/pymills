# Module:	sockets
# Date:		26th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Sockets Test Suite

...
"""

import unittest
from time import sleep

from pymills.event import filter, listener, Worker
from pymills.net.sockets import TCPClient, TCPServer

class Manager(Worker):

	client = None
	server = None
	events = 0

	def run(self):
		while self.isRunning():
			self.flush()

			self.server.poll()
			
			if self.client.connected:
				self.client.poll()

class Client(TCPClient):

	channel = "client"

	connectedFlag = False
	disconnectedFlag = False
	error = None
	dataIn = ""

	@listener("connect")
	def onCONNECT(self, host, port):
		self.connectedFlag = True

	@listener("disconnect")
	def onDISCONNECT(self):
		self.disconnectedFlag = True

	@listener("read")
	def onREAD(self, data):
		self.dataIn = data

	@listener("error")
	def onERROR(self, error):
		self.error = error

class Server(TCPServer):

	channel = "server"

	dataIn = ""
	clients = []
	errors = {}

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		self.clients.append(sock)
		self.write(sock, "Ready")

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		self.clients.remove(sock)

	@listener("read")
	def onREAD(self, sock, data):
		self.dataIn = data

	@listener("error")
	def onERROR(self, sock, error):
		self.errors[sock] = error

class SocketsTestCase(unittest.TestCase):

	def testTCPClient(self):
		"""Test sockets.TCPClient

		1. Test that a TCPClient can open a connection to
		   a given host and port
		2. Test that a TCPClient can receive data from an
		   open connection.
		3. Test that a TCPClient can write data to an open
		   connection.
		4. Test that a TCPClient can disconnect from an
		   open connection.
		"""

		manager = Manager()
		server = Server(manager, 9999)
		client = Client(manager)
		manager.server = server
		manager.client = client

		manager.start()

		try:
			#1
			client.open("localhost", 9999)
			sleep(0.1)
			self.assertTrue(client.connectedFlag)

			#2
			self.assertTrue(client.dataIn == "Ready")

			#3
			client.write("foo")
			sleep(0.1)
			self.assertTrue(server.dataIn == "foo")

			#4
			client.close()
			sleep(0.1)
			self.assertTrue(client.disconnectedFlag)
		finally:
			manager.stop()
			manager.join()

def suite():
	return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
	unittest.main()
