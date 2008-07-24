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
BUFFER_SIZE = 65536
BACKLOG = 500

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

class CloseEvent(Event):

	def __init__(self, sock=None):
		if sock is None:
			Event.__init__(self)
		else:
			Event.__init__(self, sock)

class Client(Component):

	def __init__(self, *args, **kwargs):
		super(Client, self).__init__(*args, **kwargs)

		self.host = ""
		self.port = 0
		self.ssl = False
		self.server = {}
		self.issuer = {}
		self.connected = False
		self.buffer = []

		self._fds = []
		self._closeFlag = False

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
				self.push(ErrorEvent(error), "error", self.channel)
				return

		if r:
			try:
				if self.ssl and hasattr(self, "_ssock"):
					data = self._ssock.read(BUFFER_SIZE)
				else:
					data = self._sock.recv(BUFFER_SIZE)
				if data:
					self.push(ReadEvent(data), "read", self.channel)
				else:
					self.close()
					return
			except socket.error, error:
				self.push(ErrorEvent(error), "error", self.channel)
				self.close()
				return

		if w:
			if self.buffer:
				data = self.buffer[0]
				self.send(WriteEvent(data), "write", self.channel)
			else:
				if self._closeFlag:
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
				self.push(ConnectEvent(host, port), "connect", self.channel)
			else:
				self.push(ErrorEvent("Connection timed out"), "error", self.channel)
				self.close()
		except socket.error, error:
			self.push(ErrorEvent(error), "error", self.channel)
			self.close()

	def close(self):
		if self._fds:
			self.push(CloseEvent(), "close", self.channel)
	
	def write(self, data):
		self.buffer.append(data)

	@filter("close")
	def onCLOSE(self):
		"""Close Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		if self.buffer:
			self._closeFlag = True
			return

		try:
			self._fds.remove(self._sock)
			self._sock.shutdown(2)
			self._sock.close()
		except socket.error, error:
			self.push(ErrorEvent(error), "error", self.channel)

		self.connected = False

		self.push(DisconnectEvent(), "disconnect", self.channel)

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

	@filter("write")
	def onWRITE(self, data):
		"""Write Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			if self.ssl:
				bytes = self._ssock.write(data)
			else:
				bytes = self._sock.send(data)

			if bytes < len(data):
				self.buffer[0] = data[bytes:]
			else:
				del self.buffer[0]
		except socket.error, error:
			if error[0] in [32, 107]:
				self.close()
			else:
				self.push(ErrorEvent(error), "error", self.channel)
				self.close()

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

		self.push(ConnectEvent(host, port), "connect", self.channel)

	@filter("write")
	def onWRITE(self, data):
		"""Write Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			bytes = self._sock.sendto(data, self.addr)
			if bytes < len(data):
				self.buffer[0] = data[bytes:]
			else:
				del self.buffer[0]
		except socket.error, e:
			if e[0] in [32, 107]:
				self.close()
			else:
				self.push(ErrorEvent(e), "error", self.channel)
				self.close()

class Server(Component):

	def __init__(self, *args, **kwargs):
		super(Server, self).__init__(*args, **kwargs)

		self.address = ""
		self.port = 0
		self.buffers = {}

		self._fds = []
		self._closeFlags = []

	def __getitem__(self, y):
		"x.__getitem__(y) <==> x[y]"

		return self._fds[y]

	def __contains__(self, y):
		"x.__contains__(y) <==> y in x"
	
		return y in self._fds

	def poll(self, wait=POLL_INTERVAL):
		try:
			r, w, e = select.select(self._fds, self._fds, [], wait)
		except socket.error, error:
			if error[0] == 9:
				for sock in e:
					self.close(sock)

		for sock in w:
			if self.buffers[sock]:
				data = self.buffers[sock][0]
				self.send(WriteEvent(data, sock), "write", self.channel)
			else:
				if sock in self._closeFlags:
					self.close(sock)
			
		for sock in r:
			if sock == self._sock:
				newsock, host = self._sock.accept()
				newsock.setblocking(False)
				newsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
				self._fds.append(newsock)
				self.buffers[newsock] = []
				host, port = host
				self.push(ConnectEvent(host, port, newsock), "connect", self.channel)
			else:
				try:
					data = sock.recv(BUFFER_SIZE)
				except socket.error, e:
					self.push(ErrorEvent(e, sock), "error", self.channel)
					self.close(sock)
					continue

				if not data:
					self.close(sock)
					continue

				self.push(ReadEvent(data, sock), "read", self.channel)

	def close(self, sock=None):
		if sock in self:
			self.push(CloseEvent(sock), "close", self.channel)

	def write(self, sock, data):
		self.buffers[sock].append(data)

	def broadcast(self, data):
		for sock in self._fds[1:]:
			self.write(sock, data)

	@filter("write")
	def onWRITE(self, sock, data):
		"""Write Event


		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			bytes = sock.send(data)
			if bytes < len(data):
				self.buffers[sock][0] = data[bytes:]
			else:
				del self.buffers[sock][0]
		except socket.error, e:
			if e[0] in [32, 107]:
				self.close(sock)
			else:
				self.push(ErrorEvent(e, sock), "error", self.channel)
				self.close()

	@filter("close")
	def onCLOSE(self, sock=None):
		"""Close Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		if sock:
			if not sock == self._sock:
				if self.buffers[sock]:
					self._closeFlags.append(sock)
					return

				if sock in self._closeFlags:
					self._closeFlags.remove(sock)

			try:
				sock.shutdown(2)
				sock.close()
			except socket.error, e:
				self.push(ErrorEvent(e, sock), "error", self.channel)

			self._fds.remove(sock)
			self.push(DisconnectEvent(sock), "disconnect", self.channel)
		else:
			for sock in self._fds:
				self.close(sock)


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

		self._fds.append(self._sock)

		self.address = address
		self.port = port

class UDPServer(Server):

	def __init__(self, event=None, port=1234, address="", **kwargs):
		super(UDPServer, self).__init__(event, **kwargs)

		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setsockopt(socket.SOL_SOCKET,	socket.SO_BROADCAST, 1)
		self._sock.setblocking(False)
		self._sock.bind((address, port))

		self._fds.append(self._sock)

		self.address = address
		self.port = port

	def poll(self, wait=POLL_INTERVAL):
		try:
			r, w, e = select.select(self._fds, self._fds, self._fds, wait)
		except socket.error, error:
			if error[0] == 9:
				for sock in e:
					self.close(sock)

		if w:
			for address, data in self.buffers.iteritems():
				if data:
					self.send(WriteEvent(data[0], address), "write", self.channel)

		if r:
			try:
				data, address = self._sock.recvfrom(BUFFER_SIZE)

				if not data:
					self.close()
				else:
					self.push(ReadEvent(data, address), "read", self.channel)
			except socket.error, e:
				self.push(ErrorEvent(e, self._sock), "error", self.channel)
				self.close()

	def write(self, address, data):
		if not self.buffers.has_key(address):
			self.buffers[address] = []
		self.buffers[address].append(data)

	def broadcast(self, data):
		pass

	def close(self):
		if self._fds:
			self.push(CloseEvent(), "close", self.channel)

	@filter("close")
	def onCLOSE(self):
		"""Close Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			self._fds.remove(self._sock)
			self._sock.shutdown(2)
			self._sock.close()
		except socket.error, error:
			self.push(ErrorEvent(error), "error", self.channel)

	@filter("write")
	def onWRITE(self, address, data):
		"""Write Event


		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			self._sock.sendto(data, address)
			del self.buffers[address][0]
		except socket.error, e:
			if e[0] in [32, 107]:
				self.close()
			else:
				self.push(ErrorEvent(e), "error", self.channel)
				self.close()
