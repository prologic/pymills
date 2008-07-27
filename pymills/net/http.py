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
import os
import stat
import mimetools
from time import strftime
from cStringIO import StringIO
from mimetypes import guess_type
from wsgiref.headers import Headers

import pymills
from pymills.event import listener, Event, UnhandledEvent
from pymills.event.core import Component

###
### Defaults/Constants
###

SERVER_VERSION   = "pymills/%s" % pymills.__version__
PROTOCOL_VERSION = "HTTP/1.1"
BUFFER_SIZE      = 65535

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

def quoteHTML(html):
	return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

###
### Events
###

class Request(Event): pass
class Response(Event): pass
class Stream(Event): pass

###
### Supporting Classes
###

class _Request(object):
	"""_Request(method, uri, version, headers) -> new HTTP Request object

	Request object that holds an incoming request. The URI, the version
	of the request, the headers and body. This also holds a _Response
	object ready to respond with.
	"""

	def __init__(self, method, uri, version, headers):
		"initializes x; see x.__class__.__doc__ for signature"

		self.method = method
		self.uri = uri
		self.version = version
		self.headers = headers

		self.body = StringIO()

		self.sock = None
		self.close = True

		self.res = _Response(self)

class _Response(object):
	"""_Response(req) -> new Response object

	A Response object that holds the response to
	send back to the client. This ensure that the correct data
	is sent in the correct order.
	"""

	def __init__(self, req, body=""):
		"initializes x; see x.__class__.__doc__ for signature"
		
		self.req = req

		self.headers = Headers([
			("Server", SERVER_VERSION),
			("Date", strftime("%a, %d %b %Y %H:%M:%S %Z")),
			("Content-Type", "text/html")])

		self.body = ""
		self.status = "%s 200 OK" % PROTOCOL_VERSION

	def __repr__(self):
		return "<Response %s %s>" % (
			self.__class__.__name__,
			self.headers["Content-Type"])

	def __str__(self):
		if type(self.body) == file:
			contentLength = os.fstat(self.body.fileno())[stat.ST_SIZE]
			contentType = guess_type(self.body.name)[0] or "application/octet-stream"
			body = ""
			self.headers["Content-Type"] = contentType
		else:
			body = self.body
			contentLength = len(body)

		if contentLength:
			self.headers["Content-Length"] = contentLength

		return "%s\r\n%s%s" % (self.status, str(self.headers), body)

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

	def __init__(self, *args, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		super(HTTP, self).__init__(*args, **kwargs)

		self.__commands = {}

	###
	### Event Processing
	###

	@listener("stream")
	def onSTREAM(self, res):
		data = res.body.read(BUFFER_SIZE)
		if data:
			self.write(res.req.sock, data)
			self.push(StreamEvent(res), "stream")
		else:
			res.body.close()
			if res.req.close:
				self.close(res.req.sock)
		
	@listener("response")
	def onRESPONSE(self, res):
		if type(res.body) == file:
			self.write(res.req.sock, str(res))
			self.push(StreamEvent(res), "stream")
		else:
			self.write(res.req.sock, str(res))
			if res.req.close:
				self.close(res.req.sock)

	@listener("read")
	def onREAD(self, sock, data):
		"""H.onREAD(sock, data) -> None

		Process any incoming data appending it to an internal
		buffer. Split the buffer by the standard HTTP delimiter
		\r\n and create a RawEvent per line. Any unfinished
		lines of text, leave in the buffer.
		"""

		self.__commands[sock] = None
		closeConnection = True
		data = data.strip()

		requestline, data = re.split("\r?\n", data, 1)
		words = requestline.split()

		if len(words) == 3:
			command, path, version = words
			self.__commands[sock] = command
			if version[:5] != "HTTP/":
				return self.sendError(sock, 400, "Bad request version (%r)" % version)
			try:
				base_version_number = version.split("/", 1)[1]
				version_number = base_version_number.split(".")
				# RFC 2145 section 3.1 says there can be only one "." and
				#   - major and minor numbers MUST be treated as
				#	  separate integers;
				#   - HTTP/2.4 is a lower version than HTTP/2.13, which in
				#	  turn is lower than HTTP/12.3;
				#   - Leading zeros MUST be ignored by recipients.
				if len(version_number) != 2:
					raise ValueError
				version_number = int(version_number[0]), int(version_number[1])
			except (ValueError, IndexError):
				return self.sendError(sock, 400, "Bad request version (%r)" % version)
			if version_number >= (1, 1) and PROTOCOL_VERSION >= "HTTP/1.1":
				closeConnection = False
			if version_number >= (2, 0):
				return self.sendError(sock, 505,
						  "Invalid HTTP Version (%s)" % base_version_number)
		elif len(words) == 2:
			command, path = words
			self.__commands[sock] = command
			closeConnection = True
			if command != "GET":
				return self.sendError(sock, 400,
								"Bad HTTP/0.9 request type (%r)" % command)
		elif not words:
			return
		else:
			return self.sendError(sock, 400, "Bad request syntax (%r)" % requestline)

		headers = mimetools.Message(StringIO(data), 0)

		req = _Request(command, path, version, headers)
		req.sock = sock

		conntype = headers.get('Connection', "")
		if (conntype.lower() == 'keep-alive' and
			  PROTOCOL_VERSION >= "HTTP/1.1"):
			req.close = False

		try:
			self.send(Request(req), command.lower())
		except UnhandledEvent:
			self.sendError(sock, 501, "Unsupported method (%r)" % command)

	###
	### Supporting Functions
	###

	def sendError(self, sock, code, message=None):
		"""H.sendError(sock, code, message=None) -> None
		
		Send an error reply.

		Arguments are the error code, and a detailed message.
		The detailed message defaults to the short entry matching the
		response code.

		This sends an error response (so it must be called before any
		output has been generated), and sends a piece of HTML explaining
		the error to the user.
		"""

		try:
			short, long = RESPONSES[code]
		except KeyError:
			short, long = "???", "???"

		if message is None:
			message = short

		explain = long

		content = DEFAULT_ERROR_MESSAGE % {
			"code": code,
			"message": quoteHTML(message),
			"explain": explain}

		res = _Response(None)
		res.body = content
		res.status = "%s %s" % (code, message)
		res.headers.add_header('Connection', 'close')

		if self.__commands[sock] != "HEAD" and code >= 200 and code not in (204, 304):
			self.write(sock, str(res), False)

		self.close(sock)

###
### Response Codes
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
