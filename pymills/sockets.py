# Filename: sockets.py
# Module:	sockets
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""TCP/IP and UDP Sockets

This module contains classes for TCP/IP and UDP sockets for
both servers and clients. All classes are thin layers on-top
of the standard socket library. All implementations are
non-blocking. This module relies heavily on the event module
and as such the implementations in this module are all
event-driven and should be sub-classed to do something usefull.
"""

import re
import socket
import select
from time import sleep

from event import Event, Component, filter, listener

linesep = re.compile("\r?\n")

class SocketError(Exception):

	def __init__(self, type, message):
		Exception.__init__(self)
		self.args = type, message

class ErrorEvent(Event):

	def __init__(self, error, sock=None):
		if sock is None:
			Event.__init__(self, error)
		else:
			Event.__init__(self, sock, error)

class ConnectEvent(Event):

	def __init__(self, host, port, sock=None):
		if sock is None:
			Event.__init__(self, host, port)
		else:
			Event.__init__(self, sock, host, port)

class DisconnectEvent(Event):

	def __init__(self, sock=None):
		if sock is None:
			Event.__init__(self)
		else:
			Event.__init__(self, sock)

class ReadEvent(Event):

	def __init__(self, line, sock=None):
		if sock is None:
			Event.__init__(self, line)
		else:
			Event.__init__(self, sock, line)

class WriteEvent(Event):

	def __init__(self, data, sock=None):
		if sock is None:
			Event.__init__(self, data)
		else:
			Event.__init__(self, sock, data)

class Client(Component):

	def __init__(self, event, ssl=False):
		self._buffer = ""

		self.ssl = ssl
		self.server = {}
		self.issuer = {}
		self.connected = False

	def __del__(self):
		if self.connected:
			self.close()

	def __ready__(self, wait=0.001):
		ready = select.select(
				[self._sock], [self._sock], [], wait)
		return (not ready[0] == []) and (not ready[1] == [])
		
	def __poll__(self, wait=0.001):
		return not select.select(
				[self._sock], [], [], wait)[0] == []

	def __read__(self, bufsize=512):
		try:
			if self.ssl and hasattr(self, "_ssock"):
				data = self._ssock.read(bufsize)
			else:
				data = self._sock.recv(bufsize)
		except socket.error, e:
			self.event.push(
					ErrorEvent(e),
					self.event.getChannelID("error"),
					self)
			self.close()
			return

		if not data:
			self.close()
			return

		lines = linesep.split(self._buffer + data)
		self._buffer = lines[-1]
		lines = lines[:-1]

		for line in lines:
			self.event.push(
					ReadEvent(line),
					self.event.getChannelID("read"),
					self)

	def open(self, host, port):
		try:
			self._sock.connect((host, port))
			if self.ssl:
				self._ssock = socket.ssl(self._sock)
		except socket.error, e:
			self.event.push(
					ErrorEvent(e),
					self.event.getChannelID("error"),
					self)
			return

		self._sock.setblocking(False)

		for i in range(5000):

			if self.__ready__():

				self.connected = True

				if self.ssl and hasattr(self, "_ssock"):
					self.server = re.match(
							"/C=(?P<C>.*)/ST=(?P<ST>.*)"
							"/L=(?P<L>.*)/O=(?P<O>.*)"
							"/OU=(?P<UO>.*)/CN=(?P<CN>.*)",
							self._ssock.server()).groupdict()

					self.issuer = re.match(
							"/C=(?P<C>.*)/ST=(?P<ST>.*)"
							"/L=(?P<L>.*)/O=(?P<O>.*)"
							"/OU=(?P<UO>.*)/CN=(?P<CN>.*)",
							self._ssock.issuer()).groupdict()

				self.event.push(
						ConnectEvent(host, port),
						self.event.getChannelID("connect"),
						self)

				return

		self.event.push(
				ErrorEvent("Timeout after 5s while connecting"),
				self.event.getChannelID("error"),
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
	
	@filter()
	def onDEBUG(self, event):
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

	@filter("write")
	def onWRITE(self, event, data):
		"""Write Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			if self.ssl and hasattr(self, "_ssock"):
				bytes = self._ssock.write(data)
			else:
				bytes = self._sock.send(data)
			if bytes < len(data):
				raise SocketError("Didn't write all data!")
		except socket.error, e:
			if e[0] == 32:
				self.close()
			else:
				self.event.push(
						ErrorEvent(e),
						self.event.getChannelID("error"),
						self)
		return False, event

class TCPClient(Client):

	def __init__(self, event, ssl=False):
		Client.__init__(self, event, ssl)
	
	def open(self, host, port):
		self._sock = socket.socket(
				socket.AF_INET,
				socket.SOCK_STREAM)
		Client.open(self, host, port)

class UDPClient(Client):

	def __init__(self, event, ssl=False):
		Client.__init__(self, event, ssl)

	__ready__ = lambda: None

	def open(self, host, port):
		self._sock = socket.socket(
				socket.AF_INET,
				socket.SOCK_DGRAM)

		self.addr = (host, port)

		if self.ssl:
			self._ssock = socket.ssl(self._sock)

		self._sock.setblocking(False)

		self.connected = True

		if self.ssl:
			self.server = re.match(
					"/C=(?P<C>.*)/ST=(?P<ST>.*)"
					"/L=(?P<L>.*)/O=(?P<O>.*)"
					"/OU=(?P<UO>.*)/CN=(?P<CN>.*)",
					self._ssock.server()).groupdict()

			self.issuer = re.match(
					"/C=(?P<C>.*)/ST=(?P<ST>.*)"
					"/L=(?P<L>.*)/O=(?P<O>.*)"
					"/OU=(?P<UO>.*)/CN=(?P<CN>.*)",
					self._ssock.issuer()).groupdict()

			self.event.push(
					ConnectEvent(host, port),
					self.event.getChannelID("connect"),
					self)

	@filter("write")
	def onWRITE(self, event, data):
		"""Write Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			if self.ssl and hasattr(self, "_ssock"):
				bytes = self._ssock.write(data)
			else:
				bytes = self._sock.sendto(data, self.addr)
			if bytes < len(data):
				raise SocketError("Didn't write all data!")
		except socket.error, e:
			if e[0] == 32:
				self.close()
			else:
				self.event.push(
						ErrorEvent(e),
						self.event.getChannelID("error"),
						self)
		return False, event
	
class Server(Component):

	def __init__(self, event, port, address=""):
		self._buffers = {}
		self._clients = []

	def __del__(self):
		self.close()

	def __poll__(self, wait=0.001):
		try:
			r, w, e = select.select(
					[self._sock] + self._clients, [], self._clients,
					wait)
			return r
		except socket.error, error:
			if error[0] == 9:
				for sock in e:
					self.close(sock)

	def __read__(self, bufsize=512):
		read = self.__poll__()
		for sock in read:
			if sock == self._sock:
				# New Connection
				newsock, host = self._sock.accept()
				newsock.setblocking(False)
				self._clients.append(newsock)
				self._buffers[newsock] = ""
				host, port = host
				self.event.push(
						ConnectEvent(host, port, newsock),
						self.event.getChannelID("connect"),
						self)
			else:
				# Socket has data

				try:
					data = sock.recv(bufsize)
				except socket.error, e:
					self.event.push(
							ErrorEvent(e, sock),
							self.event.getChannelID("error"),
							self)
					self.close(sock)
					continue

				if not data:
					self.close(sock)
					continue

				lines = linesep.split(
						self._buffers[sock] + data)
				self._buffers[sock] = lines[-1]
				lines = lines[:-1]

				for line in lines:
					self.event.push(
							ReadEvent(line, sock),
							self.event.getChannelID("read"),
							self)

	def close(self, sock=None):

		if sock is not None:
			try:
				sock.shutdown(2)
				sock.close()
			except socket.error, e:
				self.event.push(
						ErrorEvent(e, sock),
						self.event.getChannelID("error"),
						self)
			self._clients.remove(sock)
			self.event.push(
					DisconnectEvent(sock),
					self.event.getChannelID("disconnect"),
					self)

		else:
			for sock in self._clients:
				self.close(sock)
			try:
				self._sock.shutdown(2)
				self._sock.close()
			except socket.error, e:
				self.event.push(
						ErrorEvent(e),
						self.event.getChannelID("error"),
						self)
			self.event.push(
					DisconnectEvent(), 
					self.event.getChannelID("disconnect"),
					self)
	
	def write(self, sock, data):
		self.event.push(
				WriteEvent(data, sock),
				self.event.getChannelID("write"),
				self)
	
	def broadcast(self, data):
		for sock in self._clients:
			self.write(sock, data)

	def process(self):
		if self.__poll__():
			self.__read__()
	
	@filter()
	def onDEBUG(self, event):
		"""Debug Events

		This should be overridden by sub-classes that wish to
		process all events.
		"""

		return False, event

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		"""Connect Event

		This should be overridden by sub-classes that wish to
		do something with connection events.
		"""
	
	@listener("disconnect")
	def onDISCONNECT(self, sock):
		"""Disconnect Event

		This should be overridden by sub-classes that wish to
		do something with disconnection events.
		"""

	@listener("read")
	def onREAD(self, sock, line):
		"""Read Event

		This should be overridden by sub-classes that wish to
		do something with read events.
		"""

	@filter("write")
	def onWRITE(self, event, sock, data):
		"""Write Event

		
		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			bytes = sock.send(data)
			if bytes < len(data):
				raise SocketError("Didn't write all data!")
		except socket.error, e:
			if e[0] == 32:
				self.close(sock)
			else:
				self.event.push(
						ErrorEvent(e, sock),
						self.event.getChannelID("error"),
						self)
		return False, event

class TCPServer(Server):

	def __init__(self, event, port, address=""):
		Server.__init__(self, event, port, address)
		self._sock = socket.socket(
				socket.AF_INET, socket.SOCK_STREAM)
		self._sock.setsockopt(
				socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setblocking(False)

		self._sock.bind((address, port))
		self._sock.listen(5)

class UDPServer(Server):

	def __init__(self, event, port, address=""):
		self._buffer = ""
		self._sock = socket.socket(
				socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.setsockopt(
				socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setblocking(False)

		self._sock.bind((address, port))

	def __poll__(self, wait=0.001):
		try:
			r, w, e = select.select([self._sock], [], [], wait)
			if not r == []:
				return True
		except socket.error, error:
			if error[0] == 9:
				for sock in e:
					self.close(sock)
			return False

	def __read__(self, bufsize=512):
		if  self.__poll__():
			try:
				data, addr = self._sock.recvfrom(bufsize)
			except socket.error, e:
				self.event.push(
						ErrorEvent(e, self._sock),
						self.event.getChannelID("error"),
						self)
				self.close()
				return

			if not data:
				self.close()
				return

			lines = linesep.split(
					self._buffer + data)
			self._buffers = lines[-1]
			lines = lines[:-1]

			for line in lines:
				self.event.push(
						ReadEvent(line, self._sock),
						self.event.getChannelID("read"),
						self)
