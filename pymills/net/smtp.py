# Module:	smtp
# Date:		13th June 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Simple Mail Transfer Protocol

This module implements the Simple Mail Transfer Protocol
or commonly known as SMTP. This protocol much like other
protocols in the PyMills Library makes use of the Event
library to facilitate conformance to the protocol.
"""

import re
import sys
import socket
from tempfile import TemporaryFile

import pymills
from pymills.event import Component, Event, listener

__all__ = ["SMTP"]

###
### Supporting Functions
###

def splitLines(s, buffer):
	"""splitLines(s, buffer) -> lines, buffer

	Append s to buffer and find any new lines of text in the
	string splitting at the standard IRC delimiter \r\n. Any
	new lines found, return them as a list and the remaining
	buffer for further processing.
	"""

	x = buffer + s
	lines = x.split("\r\n")
	return lines[:-1], lines[-1]

def stripAddress(address):
	"""stripAddress(address) -> address

	Strip the leading & trailing <> from an address.
	Handy for getting FROM: addresses.
	"""

	start = address.index("<") + 1
	end = address.index(">")

	return address[start:end]

def splitTo(address):
	"""splitTo(address) -> (host, fulladdress)

	Return 'address' as undressed (host, fulladdress) tuple.
	Handy for use with TO: addresses.
	"""

	start = address.index("<") + 1
	sep = address.index("@") + 1
	end = address.index(">")

	return (address[sep:end], address[start:end],)

def getAddress(keyword, arg):
	address = None
	keylen = len(keyword)
	if arg[:keylen].upper() == keyword:
		address = arg[keylen:].strip()
		if not address:
			pass
		elif address[0] == "<" and address[-1] == ">" and address != "<>":
			# Addresses can be in the form <person@dom.com> but watch out
			# for null address, e.g. <>
			address = address[1:-1]
	return address

###
### Events
###

class RawEvent(Event):

	def __init__(self, sock, line):
		super(RawEvent, self).__init__(sock, line)

class HeloEvent(Event):

	def __init__(self, sock, hostname):
		super(HeloEvent, self).__init__(sock, hostname)

class MailEvent(Event):

	def __init__(self, sock, sender):
		super(MailEvent, self).__init__(sock, sender)

class RcptEvent(Event):

	def __init__(self, sock, recipient):
		super(RcptEvent, self).__init__(sock, recipient)

class DataEvent(Event):

	def __init__(self, sock):
		super(DataEvent, self).__init__(sock)

class RsetEvent(Event):

	def __init__(self, sock):
		super(RsetEvent, self).__init__(sock)

class NoopEvent(Event):

	def __init__(self, sock):
		super(NoopEvent, self).__init__(sock)

class QuitEvent(Event):

	def __init__(self, sock):
		super(QuitEvent, self).__init__(sock)

class MessageEvent(Event):

	def __init__(self, sock, mailfrom, rcpttos, data):
		super(MessageEvent, self).__init__(sock, mailfrom, rcpttos, data)

###
### Protocol Class
###

class SMTP(Component):
	"""SMTP(event) -> new smtp object

	Create a new smtp object which implements the SMTP
	protocol. Note this doesn't actually do anything
	usefull unless used in conjunction with
	pymills.sockets.TCPServer.

	See: examples/net/smtpd.py
	"""

	COMMAND = 0
	DATA = 1

	def __init__(self, *args, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		super(SMTP, self).__init__(*args, **kwargs)

		self.__buffers = {}

		self.__states = {}

		self.__greeting = None
		self.__mailfrom = None
		self.__rcpttos = []
		self.__data = None

		self.__fqdn = socket.getfqdn()

	###
	### Methods
	###

	def reset(self):
		self.__buffers = {}
		self.__states = {}
		self.__greeting = None
		self.__mailfrom = None
		self.__rcpttos = []
		self.__data = None

	def processMessage(self, sock, mailfrom, rcpttos, data):
		r =  self.send(MessageEvent(sock, mailfrom, rcpttos, data), "message")
		data.close()

		if r:
			return r[-1]

	###
	### Properties
	###

	def getFQDN(self):
		"""I.getFQDN() -> str

		Return the fully qualified domain name of this server.
		"""

		return self.__fqdn

	###
	### Event Processing
	###

	@listener("raw")
	def onRAW(self, sock, line):
		"""I.onRAW(sock, line) -> None

		Process a line of text and generate the appropiate
		event. This must not be overridden by sub-classes,
		if it is, this must be explitetly called by the
		sub-class. Other Components may however listen to
		this event and process custom SMTP events.
		"""

		if self.__state == self.COMMAND:
			if not line:
				self.write(sock, "500 Syntax error, command unrecognized\r\n")
				return

			method = None

			i = line.find(" ")
			if i < 0:
				command = line.upper()
				arg = None
			else:
				command = line[:i].upper()
				arg = line[i+1:].strip()

			method = getattr(self, "smtp" + command, None)

			if not method:
				self.write(sock, "502 Command not implemented\r\n")
			else:
				method(sock, arg)
		else:
			if self.__state != self.DATA:
				self.write(sock, "451 Internal confusion\r\n")
				return

			if line and re.match("^\.$", line):
					self.__data.flush()
					self.__data.seek(0)
					status = self.processMessage(sock,
							self.__mailfrom,  self.__rcpttos, self.__data)

					self.reset()

					if not status:
						self.write(sock, "250 Ok\r\n")
					else:
						self.write(sock, status + "\r\n")
			else:
				if line and line[0] == ".":
					self.__data.write(line[1:] + "\n")
				else:
					self.__data.write(line + "\n")

	###
	### SMTP and ESMTP Commands
	###

	def smtpHELO(self, sock, arg):
		if not arg:
			self.write(sock, "501 Syntax: HELO hostname\r\n")
			return

		if self.__greeting:
			self.write(sock, "503 Duplicate HELO/EHLO\r\n")
		else:
			self.__greeting = arg
			self.write(sock, "250 %s\r\n" % self.__fqdn)
			self.push(HeloEvent(sock, arg), "helo", self)

	def smtpNOOP(self, sock, arg):
		if arg:
			self.write(sock, "501 Syntax: NOOP\r\n")
		else:
			self.write(sock, "250 Ok\r\n")
			self.push(NoopEvent(sock), "noop", self)

	def smtpQUIT(self, sock, arg):
		self.write(sock, "221 Bye\r\n")
		self.close(sock)
		self.push(QuitEvent(sock), "quit", self)

	def smtpMAIL(self, sock, arg):
		address = getAddress("FROM:", arg)

		if not address:
			self.write(sock, "501 Syntax: MAIL FROM:<address>\r\n")
			return

		if self.__mailfrom:
			self.write(sock, "503 Error: nested MAIL command\r\n")
			return

		self.__mailfrom = address

		self.write(sock, "250 Ok\r\n")
		self.push(MailEvent(sock, address), "mail", self)

	def smtpRCPT(self, sock, arg):
		if not self.__mailfrom:
			self.write(sock, "503 Error: need MAIL command\r\n")
			return

		address = getAddress("TO:", arg)

		if not address:
			self.write(sock, "501 Syntax: RCPT TO: <address>\r\n")
			return

		self.__rcpttos.append(address)
		self.write(sock, "250 Ok\r\n")
		self.push(RcptEvent(sock, address), "rcpt", self)

	def smtpRSET(self, sock, arg):
		if arg:
			self.write(sock, "501 Syntax: RSET\r\n")
			return

		# Resets the sender, recipients, and data, but not the greeting
		self.__mailfrom = None
		self.__rcpttos = []
		self.__data = None
		self.__state = self.COMMAND
		self.write(sock, "250 Ok\r\n")
		self.push(RsetEvent(sock), "rset", self)

	def smtpDATA(self, sock, arg):
		if not self.__rcpttos:
			self.write(sock, "503 Error: need RCPT command\r\n")
			return

		if arg:
			self.write(sock, "501 Syntax: DATA\r\n")
			return

		self.__state = self.DATA
		self.__data = TemporaryFile()

		self.write(sock, "354 End data with <CR><LF>.<CR><LF>\r\n")
		self.push(DataEvent(sock), "data", self)

	###
	### Default Socket Events
	###

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		self.write(sock, "220 %s %s\r\n" % (self.__fqdn, pymills.__version__))

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		self.reset()

	@listener("read")
	def onREAD(self, sock, data):
		"""S.onREAD(sock, data) -> None

		Process any incoming data appending it to an internal
		buffer. Split the buffer by the standard line delimiters
		\r\n and create a RawEvent per line. Any unfinished
		lines of text, leave in the buffer.
		"""

		lines, buffer = splitLines(data, self.__buffes[sock])
		self.__buffers[sock] = buffer
		for line in lines:
			self.push(RawEvent(sock, line), "raw", self)
