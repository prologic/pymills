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
import cgi
import stat
from time import strftime
from urllib import unquote
from urlparse import urlparse
from cStringIO import StringIO
from mimetypes import guess_type
from wsgiref.headers import Headers

try:
	import cherrypy
	from cherrypy.lib.static import serve_file
	from cherrypy import HTTPError, NotFound, HTTPRedirect
except ImportError:
	cherrypy = None

import pymills
from pymills.event import *

###
### Defaults/Constants
###

SERVER_VERSION = "pymills/%s" % pymills.__version__
SERVER_PROTOCOL = "HTTP/1.1"
BUFFER_SIZE = 131072

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

COMMA_SEPARATED_HEADERS = ["ACCEPT", "ACCEPT-CHARSET", "ACCEPT-ENCODING",
		"ACCEPT-LANGUAGE", "ACCEPT-RANGES", "ALLOW", "CACHE-CONTROL",
		"CONNECTION", "CONTENT-ENCODING", "CONTENT-LANGUAGE", "EXPECT",
		"IF-MATCH", "IF-NONE-MATCH", "PRAGMA", "PROXY-AUTHENTICATE", "TE",
		"TRAILER", "TRANSFER-ENCODING", "UPGRADE", "VARY", "VIA", "WARNING",
		"WWW-AUTHENTICATE"]

###
### Supporting Functions
###

quoted_slash = re.compile("(?i)%2F")

def quoteHTML(html):
	return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

image_map_pattern = re.compile(r"[0-9]+,[0-9]+")

def parseQueryString(query_string, keep_blank_values=True):
	"""parseQueryString(query_string) -> dict

	Build a params dictionary from a query_string.
	If keep_blank_values is True (the default), keep
	values that are blank.
	"""

	if image_map_pattern.match(query_string):
		# Server-side image map. Map the coords to "x" and "y"
		# (like CGI::Request does).
		pm = query_string.split(",")
		pm = {"x": int(pm[0]), "y": int(pm[1])}
	else:
		pm = cgi.parse_qs(query_string, keep_blank_values)
		for key, val in pm.items():
			if len(val) == 1:
				pm[key] = val[0]
	return pm


def parseHeaders(data):
	environ = {}
		
	while True:
		line = data.readline()
		if not line:
			# No more data--illegal end of headers
			raise ValueError("Illegal end of headers.")
		
		if line == "\r\n":
			# Normal end of headers
			break
		
		if line[0] in " \t":
			# It's a continuation line.
			v = line.strip()
		else:
			k, v = line.split(":", 1)
			k, v = k.strip().upper(), v.strip()
			envname = "HTTP_" + k.replace("-", "_")
		
		if k in COMMA_SEPARATED_HEADERS:
			existing = environ.get(envname)
			if existing:
				v = ", ".join((existing, v))
		environ[envname] = v
	
	ct = environ.pop("HTTP_CONTENT_TYPE", None)
	if ct is not None:
		environ["CONTENT_TYPE"] = ct
	cl = environ.pop("HTTP_CONTENT_LENGTH", None)
	if cl is not None:
		environ["CONTENT_LENGTH"] = cl

	return environ, data.read()

###
### Events
###

class Request(Event):
	"""Request(Event) -> Request Event

	args: request, response
	"""

class Response(Event):
	"""Response(Event) -> Response Event

	args: request, response
	"""

class Stream(Event):
	"""Stream(Event) -> Stream Event

	args: request, response
	"""

###
### Supporting Classes
###

class _Request(object):
	"""_Request(method, path, version, qa, headers) -> new HTTP Request object

	Request object that holds an incoming request.
	"""

	script_name = ""
	protocol = (1, 1)

	def __init__(self, method, path, version, qs, headers):
		"initializes x; see x.__class__.__doc__ for signature"

		self.method = method
		self.path = self.path_info = path
		self.version = version
		self.qs = self.query_string = qs
		self.headers = headers

		self.body = StringIO()

	def __repr__(self):
		return "<Request %s %s %s>" % (self.method, self.version, self.path)

class _Response(object):
	"""_Response(sock, body="") -> new Response object

	A Response object that holds the response to
	send back to the client. This ensure that the correct data
	is sent in the correct order.
	"""

	def __init__(self, sock, body=""):
		"initializes x; see x.__class__.__doc__ for signature"

		self.sock = sock
		self.close = False
		
		self.headers = Headers([
			("Server", SERVER_VERSION),
			("Date", strftime("%a, %d %b %Y %H:%M:%S %Z")),
			("Content-Type", "text/html")])

		self.body = ""
		self.status = "200 OK"

	def __repr__(self):
		return "<Response %s %s (%d)>" % (
				self.status,
				self.headers["Content-Type"], len(self.body))

	def __call__(self):
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

		return "%s %s\r\n%s%s" % (
				SERVER_PROTOCOL,
				self.status,
				str(self.headers),
				body)


###
### Dispatcher
###

class Dispatcher(Component):

	defaults = ["index.html"]
	docroot = os.path.join(os.getcwd(), "htdocs")

	def findChannel(self, request):
		"""findChannel(request) -> channel

		Find and return an appropiate channel
		for the given request.

		The channel is found by traversing the system's event channels,
		and matching path components to successive channels in the system.

		path			channel			
		---------------------
		/				index
		/hello		hello
		/foo/			foo:index
		/foo/1		foo:index
		/foo/bar		foo:bar

		If a channel cannot be found for a given path, but there is
		a default channel, then this will be used.
		"""

		path = request.path
		if path.endswith("/"):
			target = path.rstrip("/")
			channel = "index"
		else:
			target, channel = os.path.split(path)

		defaults = [channel or "index", request.method.upper()]

		if target:
			channels = ("%s:%s" % (target, channel) for channel in defaults)
		else:
			channels = defaults

		for channel in channels:
			found = channel in self.manager.channels
			if found:
				return channel

	@filter("request")
	def onREQUEST(self, request, response):
		channel = self.findChannel(request)
		
		if channel:
			params = parseQueryString(request.qs)
			self.send(Request(request, response, **params), channel)
		else:
			path = request.path.strip("/")
			if path:
				filename = os.path.abspath(os.path.join(self.docroot, path))
			else:
				for default in self.defaults:
					filename = os.path.abspath(os.path.join(self.docroot, default))
					if os.path.exists(filename):
						break
					else:
						filename = None

			if filename:
				serve_file(filename)
				self.send(Response(response), "response")
			else:
				raise NotFound()

###
### Protocol Component
###

class HTTP(Component):
	"""HTTP() -> HTTP Component

	Create a new HTTP object which implements the HTTP
	protocol. Note this doesn"t actually do anything
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

	_requests = {}

	###
	### Event Processing
	###

	@listener("stream")
	def onSTREAM(self, response):
		data = response.body.read(BUFFER_SIZE)
		if data:
			self.write(response.sock, data)
			self.push(Stream(response), "stream")
		else:
			response.body.close()
			if response.close:
				self.close(response.sock)
		
	@listener("response")
	def onRESPONSE(self, response):
		if type(response.body) == file:
			self.write(response.sock, response())
			self.push(Stream(response), "stream")
		else:
			self.write(response.sock, response())
			if response.close:
				self.close(response.sock)

	@listener("read")
	def onREAD(self, sock, data):
		"""H.onREAD(sock, data) -> None

		Process any incoming data appending it to an internal
		buffer. Split the buffer by the standard HTTP delimiter
		\r\n and create a RawEvent per line. Any unfinished
		lines of text, leave in the buffer.
		"""

		if sock in self._requests:
			request = self._requests[sock]
			request.body.write(data)
			contentLength = int(request.headers.get("CONTENT_LENGTH", "0"))
			if not request.body.tell() == contentLength:
				return
		else:
			requestline, data = re.split("\r?\n", data, 1)
			method, path, protocol = requestline.strip().split(" ", 2)
			scheme, location, path, params, qs, frag = urlparse(path)

			if frag:
				return self.sendError(sock, 400,
						"Illegal #fragment in Request-URI.")
		
			if params:
				path = path + ";" + params
		
			# Unquote the path+params (e.g. "/this%20path" -> "this path").
			# http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html#sec5.1.2
			#
			# But note that "...a URI must be separated into its components
			# before the escaped characters within those components can be
			# safely decoded." http://www.ietf.org/rfc/rfc2396.txt, sec 2.4.2
			atoms = [unquote(x) for x in quoted_slash.split(path)]
			path = "%2F".join(atoms)
		
			# Compare request and server HTTP protocol versions, in case our
			# server does not support the requested protocol. Limit our output
			# to min(req, server). We want the following output:
			#	 request	server	 actual written   supported response
			#	 protocol   protocol  response protocol	feature set
			# a	 1.0		1.0		   1.0				1.0
			# b	 1.0		1.1		   1.1				1.0
			# c	 1.1		1.0		   1.0				1.0
			# d	 1.1		1.1		   1.1				1.1
			# Notice that, in (b), the response will be "HTTP/1.1" even though
			# the client only understands 1.0. RFC 2616 10.5.6 says we should
			# only return 505 if the _major_ version is different.
			rp = int(protocol[5]), int(protocol[7])
			sp = int(SERVER_PROTOCOL[5]), int(SERVER_PROTOCOL[7])
			if sp[0] != rp[0]:
				return self.sendError(sock, 505, "HTTP Version Not Supported")

			assert "\r\n\r\n" in data
			headers, body = parseHeaders(StringIO(data))

			request = _Request(method, path, protocol, qs, headers)
			request.body.write(body)
		
			if headers.get("EXPECT", "") == "100-continue":
				self._requests[sock] = request
				self.sendSimple(sock, 100)
				return

			contentLength = int(headers.get("CONTENT_LENGTH", "0"))
			if not request.body.tell() == contentLength:
				self._requests[sock] = request
				return

		response = _Response(sock)

		if cherrypy:
			cherrypy.request = request
			cherrypy.response = response

		# Persistent connection support
		if request.protocol == "HTTP/1.1":
			# Both server and client are HTTP/1.1
			if request.headers.get("HTTP_CONNECTION", "") == "close":
				response.close = True
		else:
			# Either the server or client (or both) are HTTP/1.0
			if request.headers.get("HTTP_CONNECTION", "") != "Keep-Alive":
				response.close = True

		request.body.seek(0)

		try:
			if not self.send(Request(request, response), "request"):
				self.sendError(sock, 501, "Unsupported method (%r)" % command,
						request, response)
		except HTTPError, error:
			self.sendError(sock, error[0], error[1], response)
		except Exception, error:
			self.sendError(sock, 500, "Internal Server Error", response)
			raise
		finally:
			if sock in self._requests:
				del self._requests[sock]

	###
	### Supporting Functions
	###

	def sendSimple(self, sock, code, message=""):
		"""H.sendSimple(sock, code, message="")

		Send a simple response.
		"""

		try:
			short, long = RESPONSES[code]
		except KeyError:
			short, long = "???", "???"

		if not message:
			message = short

		response = _Response(sock)
		response.body = message
		response.status = "%s %s" % (code, message)

		if response.status[:3] == "413" and response.protocol == "HTTP/1.1":
			# Request Entity Too Large
			response.close = True
			response.headers.add_header("Connection", "close")

		self.send(Response(response), "response")

		if response.close:
			self.close(sock)

	def sendError(self, sock, code, message=None, response=None):
		"""H.sendError(sock, code, message=None, response=None) -> None
		
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

		if response is None:
			response = _Response(sock)
		response.body = content
		response.status = "%s %s" % (code, message)
		response.headers.add_header("Connection", "close")

		self.send(Response(response), "response")

		self.close(sock)

###
### Response Codes
###

RESPONSES = {
	100: ("Continue", "Request received, please continue"),
	101: ("Switching Protocols",
		"Switching to new protocol; obey Upgrade header"),

	200: ("OK", "Request fulfilled, document follows"),
	201: ("Created", "Document created, URL follows"),
	202: ("Accepted",
		"Request accepted, processing continues off-line"),
	203: ("Non-Authoritative Information", "Request fulfilled from cache"),
	204: ("No Content", "Request fulfilled, nothing follows"),
	205: ("Reset Content", "Clear input form for further input."),
	206: ("Partial Content", "Partial content follows."),

	300: ("Multiple Choices",
		"Object has several resources -- see URI list"),
	301: ("Moved Permanently", "Object moved permanently -- see URI list"),
	302: ("Found", "Object moved temporarily -- see URI list"),
	303: ("See Other", "Object moved -- see Method and URL list"),
	304: ("Not Modified",
		"Document has not changed since given time"),
	305: ("Use Proxy",
		"You must use proxy specified in Location to access this "
		"resource."),
	307: ("Temporary Redirect",
		"Object moved temporarily -- see URI list"),

	400: ("Bad Request",
		"Bad request syntax or unsupported method"),
	401: ("Unauthorized",
		"No permission -- see authorization schemes"),
	402: ("Payment Required",
		"No payment -- see charging schemes"),
	403: ("Forbidden",
		"Request forbidden -- authorization will not help"),
	404: ("Not Found", "Nothing matches the given URI"),
	405: ("Method Not Allowed",
		"Specified method is invalid for this server."),
	406: ("Not Acceptable", "URI not available in preferred format."),
	407: ("Proxy Authentication Required", "You must authenticate with "
		"this proxy before proceeding."),
	408: ("Request Timeout", "Request timed out; try again later."),
	409: ("Conflict", "Request conflict."),
	410: ("Gone",
		"URI no longer exists and has been permanently removed."),
	411: ("Length Required", "Client must specify Content-Length."),
	412: ("Precondition Failed", "Precondition in headers is false."),
	413: ("Request Entity Too Large", "Entity is too large."),
	414: ("Request-URI Too Long", "URI is too long."),
	415: ("Unsupported Media Type", "Entity body in unsupported format."),
	416: ("Requested Range Not Satisfiable",
		"Cannot satisfy request range."),
	417: ("Expectation Failed",
		"Expect condition could not be satisfied."),

	500: ("Internal Server Error", "Server got itself in trouble"),
	501: ("Not Implemented",
		"Server does not support this operation"),
	502: ("Bad Gateway", "Invalid responses from another server/proxy."),
	503: ("Service Unavailable",
		"The server cannot process the request due to a high load"),
	504: ("Gateway Timeout",
		"The gateway server did not receive a timely response"),
	505: ("HTTP Version Not Supported", "Cannot fulfill request."),
}
