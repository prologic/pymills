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
from pymills.net.sockets import ConnectEvent, DisconnectEvent, ReadEvent, ErrorEvent, CloseEvent, WriteEvent

class Manager(Worker):

	client = None
	server = None
	events = 0

	@filter()
	def onDEBUG(self, event, *args, **kwargs):
		print event
		self.events += 1

	def run(self):
		while self.isRunning():
			self.flush()

			self.server.poll()
			
			if self.client.connected:
				self.client.poll()

class Client(TCPClient):

	__channel__ = "client"

	connectedFlag = False
	disconnectedFlag = False
	error = None
	dataIn = ""
	dataOut = ""

	@listener("connect")
	def onCONNECT(self, host, port):
		print "Client connected"
		self.connectedFlag = True

	@listener("disconnect")
	def onDISCONNECT(self):
		print "Client.onDISCONNECT:"
		self.disconnectedFlag = True

	@listener("read")
	def onREAD(self, data):
		self.dataIn = data

	@listener("error")
	def onERROR(self, error):
		self.error = error

	@listener("write")
	def onWRITE(self, data):
		self.dataOut = data

class Server(TCPServer):

	__channel__ = "server"

	dataIn = {}
	dataOut = {}
	clients = []
	errors = {}

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		self.clients.append(sock)
		self.dataIn[sock] = ""
		self.dataOut[sock] = ""
		self.write(sock, "Ready")

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		self.clients.remove(sock)
		del self.dataIn[sock]
		del self.dataOut[sock]
		print "Server.onDISCONNECT: %s" % sock

	@listener("read")
	def onREAD(self, sock, data):
		self.dataIn[sock] = data

	@listener("write")
	def onWRITE(self, sock, data):
		self.dataOut[sock] = data

	@listener("error")
	def onERROR(self, sock, error):
		self.errors[sock] = error

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

	def testWriteEvent(self):
		"""Test sockets.WriteEvent

		1. Test that WriteEvent can hold some data
		   with sock == None
		2. Test that WriteEvent can hold some data
		   for a specific socket with sock not None
		"""

		#1
		event = WriteEvent("foo")
		self.assertEquals(event[0], "foo")

		#2
		event = WriteEvent("foo", "sock")
		self.assertEquals(event[0], "sock")
		self.assertEquals(event[1], "foo")

	def testErrorEvent(self):
		"""Test sockets.ErrorEvent

		1. Test that ErrorEvent can hold an error
		   with sock == None
		2. Test that WriteEvent can hold an error
		   for a specific socket with sock not None
		"""

		#1
		event = ErrorEvent("foo")
		self.assertEquals(event[0], "foo")

		#2
		event = ErrorEvent("foo", "sock")
		self.assertEquals(event[0], "sock")
		self.assertEquals(event[1], "foo")

	def testCloseEvent(self):
		"""Test sockets.CloseEvent

		1. Test that CloseEvent can be created
		   with sock == None
		2. Test that WriteEvent can be created
		   for a specific socket with sock not None
		"""

		#1
		event = None
		try:
			event = CloseEvent()
		except:
			pass
		self.assertTrue(event)

		#2
		event = CloseEvent("sock")
		self.assertEquals(event[0], "sock")

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
		print "Channels: %s" % manager.getChannels()
		print "Handlers:"
		for handler in manager.getHandlers():
			print " %s" % handler
		print "Server: %s" % server._sock

		manager.start()

		try:
			#1
			client.open("localhost", 9999)
			print "Client: %s" % client._sock
			sleep(0.1)
			self.assertTrue(client.connectedFlag)

			#2
			self.assertTrue(client.data == "Ready\n")

			#3
			client.write("foo")
			#sleep(0.1)
			self.assertTrue(server.data == "foo")

			#4
			client.close()
			#sleep(0.1)
			#self.assertTrue(client.disconnectedFlag)

		finally:
			#client.close()
			#server.close()

			#sleep(0.01)

			manager.stop()
			manager.join()

def suite():
	return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
	unittest.main()
