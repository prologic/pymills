# Filename: sockets.py
# Module:	sockets
# Date:		26th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Sockets Test Suite

...
"""

import unittest
from time import sleep
from threading import Thread

from pymills.event import listener, Manager
from pymills.sockets import TCPClient, TCPServer, \
		SocketError, ConnectEvent, DisconnectEvent, \
		ReadEvent, WriteEvent

class ClientManager(Manager, Thread):

	def __init__(self, *args, **kwargs):
		Manager.__init__(self, *args, **kwargs)
		Thread.__init__(self)

	def start(self):
		self.running = True
		Thread.start(self)

	def stop(self):
		self.running = False

	def run(self):
		while self.running:
			self.flush()
			sleep(0.01)

class ServerManager(Manager, Thread):

	def __init__(self, *args, **kwargs):
		Manager.__init__(self, *args, **kwargs)
		Thread.__init__(self)

	def start(self):
		self.running = True
		Thread.start(self)

	def stop(self):
		self.running = False

	def run(self):
		while self.running:
			self.flush()
			sleep(0.01)


class Client(TCPClient, Thread):

	def __init__(self, *args):
		TCPClient.__init__(self, *args)
		Thread.__init__(self)

		self.connectedFlag = False
		self.disconnectedFlag = False
		self.line = None
		self.data = None

	def start(self):
		self.running = True
		Thread.start(self)

	def stop(self):
		self.running = False

	def run(self):
		while self.running:
			if self.connected:
				self.process()
			else:
				sleep(0.01)

	@listener("connect")
	def onCONNECT(self, host, port):
		self.connectedFlag = True

	@listener("disconnect")
	def onDISCONNECT(self):
		self.disconnectedFlag = True

	@listener("read")
	def onREAD(self, line):
		self.line = line

	@listener("write")
	def onWRITE(self, data):
		TCPClient.onWRITE(self, data)
		self.data = data
	
	@listener("error")
	def onERROR(self, error):
		pass

class Server(TCPServer, Thread):

	def __init__(self, *args):
		TCPServer.__init__(self, *args)
		Thread.__init__(self)

	def start(self):
		self.running = True
		Thread.start(self)

	def stop(self):
		self.running = False

	def run(self):
		while self.running:
			self.process()

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		self.write(sock, "Ready\n")

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		pass

	@listener("read")
	def onREAD(self, sock, line):
		pass

	@listener("error")
	def onERROR(self, sock, error):
		pass

class SocketsTestCase(unittest.TestCase):

	def testSocketError(self):
		"""Test sockets.SocketError

		1. Test that raising an exception of type SocketError
		   works and a type and message is shown
		"""

		try:
			raise SocketError(123, "test")
		except SocketError, error:
			#1
			self.assertEquals(error[0], 123)
			self.assertEquals(error[1], "test")

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

	def testWriteEvent(self):
		"""Test sockets.WriteEvent

		1. Test that WriteEvent can hold a line of data
		   with sock == None
		2. Test that WriteEvent can hold a line of data
		   for a specific socket with sock not None
		"""

		#1
		event = WriteEvent("foo")
		self.assertEquals(event[0], "foo")

		#2
		event = WriteEvent("foo", "sock")
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

		serverManager = ServerManager()
		clientManager = ClientManager()
		server = Server(serverManager, 10000)
		client = Client(clientManager)
		serverManager.start()
		clientManager.start()
		server.start()
		client.start()

		sleep(0.1)

		try:
			#1
			client.open("localhost", 10000)
			sleep(0.1)
			self.assertTrue(client.connectedFlag)

			#2
			self.assertTrue(client.line == "Ready\n")

			#3
			client.write("foo")
			sleep(0.1)
			self.assertTrue(client.data == "foo")

			#4
			client.close()
			sleep(0.1)
			self.assertTrue(client.disconnectedFlag)

		finally:
			#client.close()
			server.close()

			sleep(0.1)

			client.stop()
			server.stop()

			clientManager.stop()
			serverManager.stop()

def suite():
	return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
	unittest.main()
