# Filename: sockets.py
# Module:	sockets
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""TCP/IP and UDP Sockets

This module contains classes for TCP/IP and UDP sockets for
both servers and clients. All classes are thin layers on-top
of the standard socket library. All implementation are
non-blocking. This module relies heavily on the event module
and as such the implementations in this module are all
event-driven and should be sub-classes to do something usefull.
"""

import re
import socket
import select

from event import *

class SocketError(Exception):

	def __init__(self, type, message):
		pass

class ErrorEvent(Event):

	def __init__(self, error):
		Event.__init__(self,
				error=error)

class ConnectEvent(Event):

	def __init__(self, host, port):
		Event.__init__(self,
				host=host,
				port=port)

class DisconnectEvent(Event):
	pass

class ReadEvent(Event):

	def __init__(self, line):
		Event.__init__(self,
				line=line)

class WriteEvent(Event):

	def __init__(self, data):
		Event.__init__(self,
				data=data)

class TCPClient(Component):

	def __init__(self, *args):
		self._linesep = re.compile("\r?\n")
		self._buffer = ""

		self.connected = False

	def __del__(self):
		self.close()

	def __ready__(self, wait=0.01):
		ready = select.select(
				[self._sock], [self._sock], [], wait)
		return (not ready[0] == []) and (not ready[1] == [])
		
	def __poll__(self, wait=0.01):
		return not select.select(
				[self._sock], [], [], wait)[0] == []

	def __read__(self, bufsize=512):
		try:
			data = self._sock.recv(bufsize)
		except socket.error, e:
			self.event.push(
					ErrorEvent(e),
					self.event.getChannelID("error"),
					self)
			self.connected = False
			self.event.push(
					DisconnectEvent(),
					self.event.getChannelID("disconnect"),
					self)
			return

		if not data:
			self.connected = False
			self.event.push(
					DisconnectEvent(),
					self.event.getChannelID("disconnect"),
					self)
			return

		lines = self._linesep.split(self._buffer + data)
		self._buffer = lines[-1]
		lines = lines[:-1]

		for line in lines:
			self.event.push(
					ReadEvent(line),
					self.event.getChannelID("read"),
					self)

	@filter("write")
	def __write__(self, event, data):
		try:
			bytes = self._sock.send(data)
			if bytes < len(data):
				raise SocketError("Didn't write all data!")
		except socket.error, e:
			if e[0] == 32:
				self.connected = False
				self.event.push(
						DisconnectEvent(),
						self.event.getChannelID("disconnect"),
						self)
			else:
				self.event.push(
						ErrorEvent(e),
						self.event.getChannelID("error"),
						self)
		return False, event

	def open(self, host, port):
		self.host = host
		self.port = port

		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self._sock.connect((self.host, self.port))
		except socket.error, e:
			self.event.push(
					ErrorEvent(e),
					self.event.getChannelID("error"),
					self)
			return

		self._sock.setblocking(False)

		while not self.__ready__():
			pass

		self.connected = True
		self.event.push(
				ConnectEvent(host, port),
				self.event.getChannelID("connect"),
				self)

	def close(self):
		try:
			self._sock.shutdown(2)
			self._sock.close()
		except socket.error, e:
			self.event.push(
					ErrorEvent(e),
					self.event.getChannelID("error"),
					self)
		self.connected = False
		self.event.push(
				DisconnectEvent(), 
				self.event.getChannelID("disconnect"),
				self)
	
	def write(self, data):
		self.event.push(
				WriteEvent(data),
				self.event.getChannelID("write"),
				self)

	def process(self):
		if self.__poll__():
			self.__read__()
	
	def run(self):
		while self.connected:
			self.process()
	
	@filter()
	def onDEBUG(self, event, *args, **kwargs):
		"""Debug Events

		This should be overridden by sub-classes that wish to
		process all events.
		"""

		return False, event

	@listener("connect")
	def onCONNECT(self, host, port):
		"""Connect Event

		This should be overridden by sub-classes that wish to
		do something with connection events.
		"""
	
	@listener("disconnect")
	def onDISCONNECT(self):
		"""Disconnect Event

		This should be overridden by sub-classes that wish to
		do something with disconnection events.
		"""

	@listener("read")
	def onREAD(self, line):
		"""Read Event

		This should be overridden by sub-classes that wish to
		do something with read events.
		"""

	@listener("write")
	def onWRITE(self, event, data):
		"""Write Event

		This should be overridden by sub-classes that wish to
		do something with write events.
		"""

class TCPServer:

	def __init__(self, port, address = ''):
		self.port = port
		self.address = address

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setblocking(False)

		self.sock.bind((self.address, self.port))
		self.sock.listen(5)

		self.sockets = []
		self.clients = []

		self.running = True

	def close(self, sock = None):
		if sock == None:
			self.sock.shutdown(2)
			self.sock.close()
			self.running = False
		else:
			for client in self.clients:
				if client.sock == sock:
					break

			(host, port) = sock.getpeername()

			self.onDISCONNECT(sock, host, port)
			sock.close()
			self.sockets.remove(sock)
			self.clients.remove(client)

	def poll(self, wait = 0.01):
		read = [self.sock] + self.sockets
		if not wait == None:
			ready = select.select(read, [], [], wait)
		else:
			ready = select.select(read, [], [])
		return (ready[0] != [], ready[0])
	
	def process(self):
	
		(status, read) = self.poll()
		if status:
			for sock in read:
				if sock == self.sock:
					# New Connection
					(newsock, host) = self.sock.accept()
					self.sockets.append(newsock)
					(host, port) = host
					self.clients.append(_Client(newsock, self))
					self.onCONNECT(newsock, host, port)
				else:
					# Socket has data

					for client in self.clients:
						if client.sock == sock:
							break

					(host, port) = sock.getpeername()

					if not client.read():
						self.onDISCONNECT(sock, host, port)
						sock.close()
						self.sockets.remove(sock)
						self.clients.remove(client)
				
	def write(self, sock, data):
		try:
			sock.send(data)
		except socket.error, e:
			self.onERROR(e)
	
	def writeline(self, sock, line):
		self.write(sock, "%s\n" % line)
	
	def broadcast(self, data):
		for sock in self.sockets:
			self.write(sock, data)
	
	# Run

	def run(self):
		while self.running:
			self.process()
	
	# Events

	def onCONNECT(self, sock, host, port):
		pass

	def onDISCONNECT(self, sock, host, port):
		pass
	
	def onREAD(self, sock, line):
		pass

class _Client:

	def __init__(self, sock, server):
		self.sock = sock
		self.server = server
		self.buffer = ""
		self.linesep = re.compile("\r?\n")
	
	def read(self, bufsize = 512):
		try:
			data = self.sock.recv(bufsize)
		except socket.error, e:
			self.onERROR(e)

		if not data:
			return False
		else:
			lines = self.linesep.split(self.buffer + data)
			self.buffer = lines[-1]
			lines = lines[:-1]

			for line in lines:
				if not line:
					continue
				self.server.onREAD(self.sock, line)
			return True

	# Events

	def onERROR(self, error):
		pass
