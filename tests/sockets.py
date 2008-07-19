# Module:	sockets
# Date:		26th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Sockets Test Suite

...
"""

import unittest
from time import sleep

from pymills.event import listener, Worker
from pymills.net.sockets import TCPClient, TCPServer
from pymills.net.sockets import ConnectEvent, DisconnectEvent, ReadEvent

class ClientManager(Worker):

	def run(self):
		while self.isRunning():
			self.flush()
			sleep(0.01)

class ServerManager(Worker):

	def run(self):
		while self.isRunning():
			self.flush()
			sleep(0.01)

class Client(TCPClient, Worker):

	def __init__(self, *args, **kwargs):
		super(Client, self).__init__(*args, **kwargs)

		self.connectedFlag = False
		self.disconnectedFlag = False
		self.data = None

	def run(self):
		while self.isRunning():
			if self.connected:
				self.poll()
			else:
				sleep(0.01)

	@listener("connect")
	def onCONNECT(self, host, port):
		self.connectedFlag = True

	@listener("disconnect")
	def onDISCONNECT(self):
		self.disconnectedFlag = True

	@listener("read")
	def onREAD(self, data):
		self.data = data

	@listener("error")
	def onERROR(self, error):
		pass

class Server(TCPServer, Worker):

	def __init__(self, *args, **kwargs):
		super(Server, self).__init__(*args, **kwargs)

		self.data = None

	def run(self):
		while self.isRunning():
			self.process()

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		self.write(sock, "Ready\n")

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		pass

	@listener("read")
	def onREAD(self, sock, data):
		self.data = data

	@listener("error")
	def onERROR(self, sock, error):
		pass

class SocketsTestCase(unittest.TestCase):

	def testConnectEvent(self):
		"""Test sockets.ConnectEvent

		1. Test that ConnectEvent is able to hold a host and
		   port with sock == None
		2. Test that ConnectEvent is able to hold a host and
		   port for a specific socket with sock not None
		"""

		#1
		event = ConnectEvent("localhost", 1234)
		self.assertEquals(event[0], "localhost")
		self.assertEquals(event[1], 1234)

		#2
		event = ConnectEvent("localhost", 1234, "sock")
		self.assertEquals(event[0], "sock")
		self.assertEquals(event[1], "localhost")
		self.assertEquals(event[2], 1234)

	def testDisconnectEvent(self):
		"""Test sockets.DisconnectEvent

		1. Test that DisconnectEvent works with sock == None
		2. Test that DisconnectEvent works for a specific
		   sock with sock not None
		"""

		#1
		event = DisconnectEvent()

		#2
		event = DisconnectEvent("sock")
		self.assertEquals(event[0], "sock")

	def testReadEvent(self):
		"""Test sockets.ReadEvent

		1. Test that ReadEvent can hold a line of text
		   with sock == None
		2. Test that ReadEvent can hold a line of test
		   for a specific socket with sock not None
		"""

		#1
		event = ReadEvent("foo")
		self.assertEquals(event[0], "foo")

		#2
		event = ReadEvent("foo", "sock")
		self.assertEquals(event[0], "sock")
		self.assertEquals(event[1], "foo")

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

		serverManager = ServerManager(autoStart=True)
		clientManager = ClientManager(autoStart=True)
		server = Server(serverManager, 9999)
		client = Client(clientManager)

		server.start()

		try:
			#1
			client.open("localhost", 9999)
			client.start()
			sleep(0.1)
			self.assertTrue(client.connectedFlag)

			#2
			self.assertTrue(client.data == "Ready\n")

			#3
			client.write("foo")
			sleep(0.1)
			self.assertTrue(server.data == "foo")

			#4
			client.close()
			sleep(0.01)
			self.assertTrue(client.disconnectedFlag)

		finally:
			client.close()
			server.close()

			sleep(0.01)

			client.stop()
			client.join()
			server.stop()
			server.join()

			clientManager.stop()
			clientManager.join()
			serverManager.stop()
			serverManager.join()

def suite():
	return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
	unittest.main()
