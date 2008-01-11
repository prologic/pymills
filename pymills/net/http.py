# Filename: http.py
# Module:	http
# Date:		13th September 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Hyper Text Transfer Protocol

This module implements the Hyper Text Transfer Protocol
or commonly known as HTTP. This protocol much like other
protocols in the pymills Library makes use of the event
library to facilitate conformance to the protocol.

This module can be used in both server and client
implementations.
"""

import re
import sys
import time
import socket
import mimetools

from pymills.event import filter, listener, \
		Component, Event

###
### Constants
###

DEFAULT_ERROR_MESSAGE = """\
<head>
<title>Error response</title>
</head>
<body>
<h1>Error response</h1>
<p>Error code %(code)d.
<p>Message: %(message)s.
<p>Error code explanation: %(code)s = %(explain)s.
</body>
"""

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

###
### Evenets
###

class RawEvent(Event):

	def __init__(self, sock, line):
		super(RawEvent, self).__init__(sock, line)

class ErrorEvent(Event):

	def __init__(self, code, msg):
		super(ErrorEvent, self).__init__(code, msg)
###
### Protocol Class
###

class HTTP(Component):
	"""HTTP(event) -> new HTTP object

	Create a new HTTP object which implements the HTTP
	protocol. Note this doesn't actually do anything
	usefull unless used in conjunction with either:
	 * pymills.net.sockets.TCPClient or
	 * pymills.net.sockets.TCPServer

	Sub-classes that wish to do something usefull with
	events that are processed and generated, must have
	filters/listeners associated with them. For instance,
	to do something with ... events:

	{{{
	#!python
	class Client(HTTP):

		@listener("...")
		def on...(self, ...):
			...
	}}}

	The available events that are processed and generated
	are pushed onto channels associated with that event.
	They are:
	 * ...
	"""

	def __init__(self, *args):
		"initializes x; see x.__class__.__doc__ for signature"

		super(HTTP, self).__init__(*args)

		self._buffer = ""

	###
	### Properties
	###

	###
	### HTTP Commands
	###

	def GET(self, path, version="HTTP/1.1"):
		"""H.GET(path, version="HTTP/1.1") -> None

		Send a GET request
		"""

		e = WriteEvent("GET %s %s\n" % (path, version))
		self.push(e, "write")

	###
	### Event Processing
	###

	@listener("read")
	def onREAD(self, sock, data):
		"""H.onREAD(sock, data) -> None

		Process any incoming data appending it to an internal
		buffer. Split the buffer by the standard HTTP delimiter
		\r\n and create a RawEvent per line. Any unfinished
		lines of text, leave in the buffer.
		"""

		lines, buffer = splitLines(data, self._buffer)
		self._buffer = buffer
		for line in lines:
			self.push(RawEvent(sock, line), "raw", self)

	@listener("raw")
	def onRAW(self, sock, line):
		"""H.onRAW(line) -> None

		Process a line of text and generate the appropiate
		event. This must not be overridden by sub-classes,
		if it is, this must be explitetly called by the
		sub-class. Other Components may however listen to
		this event and process custom HTTP events.
		"""

		tokens = line.split(" ")

		if len(tokens) == 3:
			command, path, version = tokens
			m = re.match("HTTP/(1)\.([01])", version)
			if m is None:
				e = ErrorEvent(
						400,
						"Bad request version (%r)" % version)
				self.push(e, "error")

		elif len(tokens) == 2:
			command, path = tokens
			if not command == "GET":
				e = ErrorEvent(
						400,
						"Bad HTTP/0.9 request type (%r)" % command)
				self.push(e, "error")
		else:
			e = ErrorEvent(
					400,
					"Bad request syntax (%r)" % line)
			self.push(e, "error")

	###
	### Default Events
	###

###
### Error and Reply codes
###

RESPONSES = {
	100: ('Continue', 'Request received, please continue'),
	101: ('Switching Protocols',
		'Switching to new protocol; obey Upgrade header'),

	200: ('OK', 'Request fulfilled, document follows'),
	201: ('Created', 'Document created, URL follows'),
	202: ('Accepted',
		'Request accepted, processing continues off-line'),
	203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
	204: ('No Content', 'Request fulfilled, nothing follows'),
	205: ('Reset Content', 'Clear input form for further input.'),
	206: ('Partial Content', 'Partial content follows.'),

	300: ('Multiple Choices',
		'Object has several resources -- see URI list'),
	301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
	302: ('Found', 'Object moved temporarily -- see URI list'),
	303: ('See Other', 'Object moved -- see Method and URL list'),
	304: ('Not Modified',
		'Document has not changed since given time'),
	305: ('Use Proxy',
		'You must use proxy specified in Location to access this '
		'resource.'),
	307: ('Temporary Redirect',
		'Object moved temporarily -- see URI list'),

	400: ('Bad Request',
		'Bad request syntax or unsupported method'),
	401: ('Unauthorized',
		'No permission -- see authorization schemes'),
	402: ('Payment Required',
		'No payment -- see charging schemes'),
	403: ('Forbidden',
		'Request forbidden -- authorization will not help'),
	404: ('Not Found', 'Nothing matches the given URI'),
	405: ('Method Not Allowed',
		'Specified method is invalid for this server.'),
	406: ('Not Acceptable', 'URI not available in preferred format.'),
	407: ('Proxy Authentication Required', 'You must authenticate with '
		'this proxy before proceeding.'),
	408: ('Request Timeout', 'Request timed out; try again later.'),
	409: ('Conflict', 'Request conflict.'),
	410: ('Gone',
		'URI no longer exists and has been permanently removed.'),
	411: ('Length Required', 'Client must specify Content-Length.'),
	412: ('Precondition Failed', 'Precondition in headers is false.'),
	413: ('Request Entity Too Large', 'Entity is too large.'),
	414: ('Request-URI Too Long', 'URI is too long.'),
	415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
	416: ('Requested Range Not Satisfiable',
		'Cannot satisfy request range.'),
	417: ('Expectation Failed',
		'Expect condition could not be satisfied.'),

	500: ('Internal Server Error', 'Server got itself in trouble'),
	501: ('Not Implemented',
		'Server does not support this operation'),
	502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
	503: ('Service Unavailable',
		'The server cannot process the request due to a high load'),
	504: ('Gateway Timeout',
		'The gateway server did not receive a timely response'),
	505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}
