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
import time
import errno
import socket
import select
from cStringIO import StringIO

from pymills.event import Event, Component, filter

POLL_INTERVAL = 0.000001
CONNECT_TIMEOUT = 5
BUFFER_SIZE = 1024
BACKLOG = 10

class SocketError(Exception): pass

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

	def __init__(self, data, sock=None):
		if sock is None:
			Event.__init__(self, data)
		else:
			Event.__init__(self, sock, data)

class WriteEvent(Event):

	def __init__(self, data, sock=None):
		if sock is None:
			Event.__init__(self, data)
		else:
			Event.__init__(self, sock, data)

class Client(Component):

	def __init__(self, *args, **kwargs):
		super(Client, self).__init__(*args, **kwargs)

		self.host = ""
		self.port = 0
		self.ssl = False
		self.server = {}
		self.issuer = {}
		self.connected = False
		self.buffer = StringIO()

		self._fds = []

	def __del__(self):
		if self.connected:
			self.close()

	def poll(self, wait=POLL_INTERVAL):
		try:
			r, w, e = select.select(self._fds, self._fds, [], wait)
		except socket.error, error:
			if error[0] == errno.EBADF:
				self.connected = False
				return
		except select.error, error:
			if error[0] == 4:
				pass
			else:
				self.push(ErrorEvent(error), "error")
				return

		if (r or w) and not self.connected:
			self.connected = True
			self.push(ConnectEvent(self.host, self.port), "connect")
			return
			
		if r:
			try:
				if self.ssl and hasattr(self, "_ssock"):
					data = self._ssock.read(BUFFER_SIZE)
				else:
					data = self._sock.recv(BUFFER_SIZE)
				if data:
					self.push(ReadEvent(data), "read")
				else:
					self.close()
					return
			except socket.error, error:
				self.push(ErrorEvent(error), "error", self)
				self.close()
				return

		if w:
			try:
				data = self.buffer.read(BUFFER_SIZE)

				if data:
					if self.ssl:
						bytes = self._ssock.write(data)
					else:
						bytes = self._sock.send(data)

					if bytes < len(data):
						delta = (BUFFER_SIZE - bytes) * -1
						self.buffer.seek(delta, 1)
			except socket.error, error:
				if error[0] in [32, 107]:
					self.close()
				else:
					self.push(ErrorEvent(error), "error")
					self.close()

	def open(self, host, port, ssl=False):
		self.ssl = ssl
		self.host = host
		self.port = port

		try:
			try:
				self._sock.connect((host, port))
			except socket.error, error:
				if error[0] == errno.EINPROGRESS:
					pass

			if self.ssl:
				self._ssock = socket.ssl(self._sock)
			
			r, w, e = select.select([], self._fds, [], CONNECT_TIMEOUT)
			if w:
				self.connected = True
				self.push(ConnectEvent(host, port), "connect")
			else:
				self.push(ErrorEvent("Connection timed out"), "error")
				self.close()
		except socket.error, error:
			self.push(ErrorEvent(error), "error")
			self.close()

	def close(self):
		try:
			self._sock.shutdown(2)
			self._sock.close()
		except socket.error, error:
			self.push(ErrorEvent(error), "error")
		self.connected = False
		self.push(DisconnectEvent(), "disconnect")

	def write(self, data):
		self.buffer.seek(0, 2)
		self.buffer.write(data)
		self.buffer.seek(0)

class TCPClient(Client):

	def __init__(self, *args, **kwargs):
		super(TCPClient, self).__init__(*args, **kwargs)

	def open(self, host, port, ssl=False, bind=None):
		self._sock = socket.socket(
				socket.AF_INET,
				socket.SOCK_STREAM)
		self._sock.setblocking(False)
		self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

		if bind is not None:
			self._sock.bind((bind, 0))

		self._fds.append(self._sock)

		super(TCPClient, self).open(host, port, ssl)

class UDPClient(Client):

	def __init__(self, event):
		super(UDPClient, self).__init__(event)

	def open(self, host, port):
		self._sock = socket.socket(
				socket.AF_INET,
				socket.SOCK_DGRAM)

		self.host = host
		self.port = port
		self.addr = (host, port)

		self._sock.setblocking(False)

		self.connected = True

		self.push(ConnectEvent(host, port), "connect")

	@filter("write")
	def onWRITE(self, data):
		"""Write Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			bytes = self._sock.sendto(data, self.addr)
			if bytes < len(data):
				raise SocketError("Didn't write all data!")
		except socket.error, e:
			if e[0] in [32, 107]:
				self.close()
			else:
				self.push(ErrorEvent(e), "error", self)
				self.close()

class Server(Component):

	def __init__(self, *args, **kwargs):
		super(Server, self).__init__(*args, **kwargs)

		self._socks = []

	def __del__(self):
		self.close()

	def __poll__(self, wait=POLL_INTERVAL):
		try:
			r, w, e = select.select(self._socks, [], self._socks, wait)
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
				self._socks.append(newsock)
				host, port = host
				self.push(
						ConnectEvent(host, port, newsock),
						"connect", self)
			else:
				# Socket has data

				try:
					data = sock.recv(bufsize)
				except socket.error, e:
					self.push(ErrorEvent(e[1], sock), "error", self)
					self.close(sock)
					continue

				if not data:
					self.close(sock)
					continue

				self.push(
						ReadEvent(data, sock), "read", self)

	def close(self, sock=None):
		if sock is not None:
			try:
				sock.shutdown(2)
				sock.close()
			except socket.error, e:
				self.push(ErrorEvent(e[1], sock), "error", self)
			self._socks.remove(sock)
			self.push(DisconnectEvent(sock), "disconnect", self)

		else:
			for sock in self._socks:
				self.close(sock)

	def write(self, sock, data):
		self.push(WriteEvent(data, sock), "write", self)

	def broadcast(self, data):
		for sock in self._socks[1:]:
			self.write(sock, data)

	def process(self):
		self.__read__()

	@filter("write")
	def onWRITE(self, sock, data):
		"""Write Event


		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			bytes = sock.send(data)
			if bytes < len(data):
				raise SocketError("Didn't write all data!")
		except socket.error, e:
			if e[0] in [32, 107]:
				self.close(sock)
			elif e[0] == 35:
				self.push(WriteEvent(data, sock), "write", self)
			else:
				self.push(ErrorEvent(e[1], sock), "error", self)
				self.close()

class TCPServer(Server):

	def __init__(self, event=None, port=1234, address="", **kwargs):
		super(TCPServer, self).__init__(event, **kwargs)

		self._sock = socket.socket(
				socket.AF_INET, socket.SOCK_STREAM)
		self._sock.setsockopt(
				socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setblocking(False)
		self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

		self._sock.bind((address, port))
		self._sock.listen(BACKLOG)

		self._socks.append(self._sock)

class UDPServer(Server):

	def __init__(self, event, port, address=""):
		super(UDPServer, self).__init__(event)

		self._sock = socket.socket(
				socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.setsockopt(
				socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setblocking(False)

		self._sock.bind((address, port))

	def __poll__(self, wait=POLL_INTERVAL):
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
				self.push(ErrorEvent(e[1], self._sock), "error", self)
				self.close()
				return

			if not data:
				self.close()
				return

			self.push(
					ReadEvent(data, self._sock), "read", self)
