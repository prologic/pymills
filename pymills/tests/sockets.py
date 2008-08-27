# Module:	sockets
# Date:		26th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Sockets Test Suite

...
"""

import unittest
from time import sleep

from pymills import event
from pymills.event import *
from pymills.net.sockets import TCPClient, TCPServer
from pymills.net.sockets import UDPClient, UDPServer

class Manager(Worker):

	client = None
	server = None
	events = 0

	def run(self):
		while self.running:
			self.flush()

			self.server.poll()
			
			if self.client.connected:
				self.client.poll()

class Client(Component):

	channel = "client"

	connected = False
	disconnected = False
	error = None
	data = ""

	@listener("connect")
	def onCONNECT(self, host, port):
		self.connected = True

	@listener("disconnect")
	def onDISCONNECT(self):
		self.disconnected = True

	@listener("read")
	def onREAD(self, data):
		self.data = data

	@listener("error")
	def onERROR(self, error):
		self.error = error

class Server(Component):

	channel = "server"

	data = ""
	errors = {}
	server = None

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		self.server.write(sock, "Ready")

	@listener("read")
	def onREAD(self, sock, data):
		self.data = data

	@listener("error")
	def onERROR(self, sock, error):
		self.errors[sock] = error

class SocketsTestCase(unittest.TestCase):

	def testTCPClientServer(self):
		"""Test sockets.TCPClient and sockets.TCPServer

		Test that communication between a TCPClient and
		TCPServer work correctly.
		"""

		manager = Manager()
		tcpserver = TCPServer(9999, channel="server")
		tcpclient = TCPClient(channel="client")
		server = Server()
		client = Client()
		manager += tcpserver
		manager += tcpclient
		manager += server
		manager += client
		manager.server = tcpserver
		server.server = tcpserver
		manager.client = tcpclient

		manager.start()

		try:
			tcpclient.open("localhost", 9999)
			sleep(0.1)
			self.assertTrue(client.connected)

			self.assertTrue(client.data == "Ready")

			tcpclient.write("foo")
			sleep(0.1)
			self.assertTrue(server.data == "foo")

			tcpclient.close()
			sleep(0.1)
			self.assertTrue(client.disconnected)
		finally:
			manager.stop()
			manager.join()

	def testUDPClientServer(self):
		"""Test sockets.UDPClient and sockets.UDPServer

		Test that communication between a UDPClient and
		UDPServer work correctly.
		"""

		manager = Manager()
		udpserver = UDPServer(9999, channel="server")
		udpclient = UDPClient(10000, channel="client")
		server = Server()
		client = Client()
		manager += udpserver
		manager += udpclient
		manager += server
		manager += client
		manager.server = udpserver
		server.server = udpserver
		manager.client = udpclient

		manager.start()

		try:
			udpclient.connected = True
			#udpclient.open("localhost", 9999)
			#sleep(0.1)
			#self.assertTrue(client.connected)

			udpclient.write(("localhost", 9999), "foo")
			sleep(0.1)
			self.assertTrue(server.data == "foo")
		finally:
			manager.stop()
			manager.join()


def suite():
	return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
	unittest.main()
