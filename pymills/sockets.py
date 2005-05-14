# Filename: Sockets.py
# Module:   Sockets
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate$
# $Author$
# $Id$

"""Sockets Module"""

import re
import sys
import time
import socket
import select
import string

class _Traffic:

	def __init__(self):
		self._in = 0
		self._out = 0
	
	def _update(self, data, direction):
		if direction == 1:
			self._out += len(data)
		elif direction == -1:
			self._in += len(data)
	
	def _get(self):
		return (self._in, self._out)
	
class TCPClient:

	def __init__(self):
		self.connected = False
		self.linesep = re.compile("\r?\n")
		self.buffer = ""

		self._traffic = _Traffic()

	def __del__(self):
		self.close()
	
	def getTraffic(self):
		return self._traffic._get()

	def open(self, host, port):
		self.host = host
		self.port = port

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self.sock.connect((self.host, self.port))
		except socket.error, e:
			self.onERROR(e)
			sys.stderr.write("*** ERROR: %s\n" % str(e))
			sys.stderr.flush()
			return False

		self.sock.setblocking(False)

		while not self._ready():
			pass

		self.connected = True
		self.onCONNECT(host, port)

		return True

	def close(self):
		try:
			self.sock.shutdown(2)
			self.sock.close()
			self.onDISCONNECT()
		except socket.error, e:
			self.onERROR(e)
		self.connected = False
	
	def _ready(self, wait = 0.01):
		if not wait == None:
			ready = select.select([self.sock], [self.sock], [], wait)
		else:
			ready = select.select([self.sock], [self.sock], [])
		read = ready[0]
		write = ready[1]
		return (not read == []) or (not write == [])
		
	def _poll(self, wait = 0.01):
		if not wait == None:
			ready = select.select([self.sock], [], [], wait)
		else:
			ready = select.select([self.sock], [], [])
		read = ready[0]
		return read != []
	
	def process(self):
		if self._poll():
			self._read()
	
	def _read(self, bufsize = 512):
		try:
			data = self.sock.recv(bufsize)
		except socket.error, e:
			data = None
			self.onERROR(e)
			sys.stderr.write("*** ERROR: %s\n" % str(e))
			sys.stderr.flush()

		if not data:
			self.connected = False
			self.onDISCONNECT()
		else:
			self._traffic._update(data, -1)

			lines = self.linesep.split(self.buffer + data)
			self.buffer = lines[-1]
			lines = lines[:-1]

			for line in lines:
				if not line:
					continue
				self.onREAD(line)

	def write(self, data):
		try:
			bytes = self.sock.send(data)
			if bytes < len(data):
				sys.stdout.write("*** ERROR: Didn't write all data!\n")
			self._traffic._update(data, 1)
			sys.stdout.write("O: %s" % data)
			sys.stdout.write("%s\n" % str(map(ord, data)))
			sys.stdout.flush()
		except socket.error, e:
			if e[0] == 32:
				self.connected = False
			else:
				sys.stderr.write("*** ERROR: %s\n" % str(e))
				sys.stderr.flush()
	
	# Run

	def run(self):
		while self.connected:
			self.process()
	
	# Events

	def onERROR(self, error):
		pass
	
	def onCONNECT(self, host, port):
		sys.stdout.write("Connected to %s:%s\n" % (host, port))

	def onDISCONNECT(self):
		sys.stdout.write("Disconnected\n")
	
	def onREAD(self, line):
		sys.stdout.write("[%s]: %s" % (time.strftime("%H:%M:%S"), line))

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
			sys.stderr.write("*** ERROR: %s\n" % str(e))
			sys.stderr.flush()
	
	def broadcast(self, data):
		for sock in self.sockets:
			self.write(sock, data)
	
	# Run

	def run(self):
		while self.running:
			self.process()
	
	# Events

	def onCONNECT(self, sock, host, port):
		sys.stdout.write("Connection from %s:%s\n" % (host, port))
		sys.stdout.flush()

	def onDISCONNECT(self, sock, host, port):
		sys.stdout.write("Disconnection from %s:%s\n" % (host, port))
		sys.stdout.flush()
	
	def onREAD(self, sock, line):
		sys.stdout.write("I: %s" % line)
		sys.stdout.flush()

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
			sys.stderr.write("*** ERROR: %s\n" % str(e))
			sys.stderr.flush()

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
