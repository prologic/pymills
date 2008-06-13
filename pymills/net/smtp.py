# Filename: smtp.py
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
import socket

import pymills
from pymills.event import Component, Event, listener

__all__ = ["SMTP"]

###
### Supporting Functions
###

linesep = re.compile("\r?\n")

def splitLines(s, buffer):
	"""splitLines(s, buffer) -> lines, buffer

	Append s to buffer and find any new lines of text in the
	string splitting at the standard IRC delimiter \r\n. Any
	new lines found, return them as a list and the remaining
	buffer for further processing.
	"""

	lines = linesep.split(buffer + s)
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
### Evenets
###

class RawEvent(Event):

	def __init__(self, sock, line):
		super(RawEvent, self).__init__(sock, line)

class HeloEvent(Event):

	def __init__(self, sock, hostname):
		super(HeloEvent, self).__init__(sock, hostname)

class MailFromEvent(Event):

	def __init__(self, sock, sender):
		super(MailFromEvent, self).__init__(sock, sender)

class RcptToEvent(Event):

	def __init__(self, sock, recipient):
		super(MailFromEvent, self).__init__(sock, recipient)

class ResetEvent(Event):

	def __init__(self, sock):
		super(ResetEvent, self).__init__(sock)

class NoOpEvent(Event):

	def __init__(self, sock):
		super(NoOpEvent, self).__init__(sock)

class QuitEvent(Event):

	def __init__(self, sock):
		super(QuitEvent, self).__init__(sock)

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

		self.__buffer = ""
		self.__state = self.COMMAND
		self.__greeting = False
		self.__mailfrom = None
		self.__rcpttos = []
		self.__data = None
		self.__fqdn = socket.getfqdn()

	###
	### Methods
	###

	def reset(self):
		self.__buffer = ""
		self.__state = self.COMMAND
		self.__greetings = False
		self.__mailfrom = None
		self.__rcpttos = []
		self.__date = None

	def processMessage(selfk, sock, data):
		pass

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
				self.write(sock, "500 Syntax error, command unrecognized")
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
				self.write(sock, "502 Command not implemented")
			else:
				method(sock, arg)
		else:
			if self.__state != self.DATA:
				self.write(sock, "451 Requested action aborted: local error in processing")
				return

			if line and line[0] == ".":
				self.__date.write(line[1:] + "\n")
			else:
				self.__date.write(line + "\n")

			status = self.processMessage(sock,
					self.__mailfrom,  self.__rcpttos, self.__data)

			self.reset()

			if not status:
				self.write(sock, "250 Ok")
			else:
				self.write(sock, status)

	###
	### SMTP and ESMTP Commands
	###

	def smtpHELO(self, sock, arg):
		if not arg:
			self.write(sock, "501 Syntax: HELO hostname")
			return

		if self.__greeting:
			self.write(sock, "503 Duplicate HELO/EHLO")
		else:
			self.__greeting = arg
			self.write(sock, "250 %s" % self.__fqdn)

	def smtpNOOP(self, sock, arg):
		if arg:
			self.write(sock, "501 Syntax: NOOP")
		else:
			self.write(sock, "250 Ok")

	def smtpQUIT(self, sock, arg):
		self.write(sock, "221 Bye")
		self.close(sock)

	def smtpMAIL(self, sock, arg):
		address = getAddress("FROM:", arg)
		if not address:
			self.write("501 Syntax: MAIL FROM:<address>")
			return
		if self.__mailfrom:
			self.write("503 Error: nested MAIL command")
			return
		self.__mailfrom = address
		print >> DEBUGSTREAM, "sender:", self.__mailfrom
		self.write("250 Ok")

	def smtp_RCPT(self, arg):
		print >> DEBUGSTREAM, "===> RCPT", arg
		if not self.__mailfrom:
			self.write("503 Error: need MAIL command")
			return
		address = self.__getaddr("TO:", arg)
		if not address:
			self.write("501 Syntax: RCPT TO: <address>")
			return
		self.__rcpttos.append(address)
		print >> DEBUGSTREAM, "recips:", self.__rcpttos
		self.write("250 Ok")

	def smtp_RSET(self, arg):
		if arg:
			self.write("501 Syntax: RSET")
			return

		# Resets the sender, recipients, and data, but not the greeting
		self.__mailfrom = None
		self.__rcpttos = []
		self.__data = ""
		self.__state = self.COMMAND
		self.write("250 Ok")

	def smtp_DATA(self, arg):
		if not self.__rcpttos:
			self.write("503 Error: need RCPT command")
			return
		if arg:
			self.write("501 Syntax: DATA")
			return
		self.__state = self.DATA
		self.set_terminator("\r\n.\r\n")
		self.write("354 End data with <CR><LF>.<CR><LF>")

	###
	### Default Socket Events
	###

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		self.write(sock, "220 %s %s\r\n" % (self.__fqdn, pymills.__version__))

	@listener("read")
	def onREAD(self, sock, data):
		"""S.onREAD(sock, data) -> None

		Process any incoming data appending it to an internal
		buffer. Split the buffer by the standard line delimiters
		\r\n and create a RawEvent per line. Any unfinished
		lines of text, leave in the buffer.
		"""

		lines, buffer = splitLines(data, self._buffer)
		self._buffer = buffer
		for line in lines:
			self.push(RawEvent(sock, line), "raw", self)

	###
	### Default SMTP Events
	###

	@listener("helo")
	def onHELO(self, sock):
		"""HELO Event

		This is a default event for responding to HELO Events.
		Sub-classes may override this, but be sure to respond to
		HELO Events by either explitetly calling this method
		or sending your own appropiate reponse.
		"""

		self.write(sock, "250 %s\r\n" % self.getFQDN())

	@listener("noop")
	def onNOOP(self, sock):
		"""NOOP Event

		This is a default event for responding to NOOP Events.
		Sub-classes may override this, but be sure to respond to
		NOOP Events by either explitetly calling this method
		or sending your own appropiate reponse.
		"""

		self.write("250 OK\r\n")

	@listener("quit")
	def onQUIT(self, sock):
		"""QUIT Event

		This is a default event for responding to QUIT Events.
		Sub-classes may override this, but be sure to respond to
		QUIT Events by either explitetly calling this method
		or sending your own appropiate reponse.
		"""

		self.write(sock, "221 Bye\r\n")
		self.close(sock)

###
### Errors and Numeric Replies
###

replies = {
		220: "%s Service ready",
		221: "%s Service closing transmission channel",
		250: "Requested mail action okay, completed",
		251: "User not local; will forward to %s",

		354: "Start mail input; end with <CRLF>.<CRLF>",
		  
		421: "%s Service not available,",
		450: "Requested mail action not taken: mailbox unavailable",
		451: "Requested action aborted: local error in processing",
		452: "Requested action not taken: insufficient system storage",
		  
		500: "Syntax error, command unrecognized",
		501: "Syntax error in parameters or arguments",
		502: "Command not implemented",
		503: "Bad sequence of commands",
		504: "Command parameter not implemented",
		550: "Requested action not taken: mailbox unavailable",

		551: "User not local; please try %s",
		552: "Requested mail action aborted: exceeded storage allocation",
		553: "Requested action not taken: mailbox name not allowed",
		554: "Transaction failed",
		}
