# Filename: irc.py
# Module:	irc
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Internet Relay Chat Protocol

This module implements the Internet Relay Chat Protocol
or commonly known as IRC. This protocol much like other
protocols in the PyMills Library makes use of the Event
library to facilitate conformance to the protocol.

This module can be used in both server and client
implementations.
"""

import re
import time

from event import Component, Event, listener

###
### Supporting Functions
###

def strip(s, color=False):
	"""strip(s, color=False) -> str

	Strips the : from the start of a string
	and optionally also strips all colors if
	color is True.
	"""

	if len(s) > 0:
		if s[0] == ":":
			s = s[1:]
	if color:
		s = s.replace("\x01", "")
		s = s.replace("\x02", "")
	return s
	
def sourceJoin(source):
	"""sourceJoin(source) -> str

	Join a source previously split by sourceSplit
	and join it back together inserting the ! and @
	appropiately.
	"""

	return "%s!%s@%s" % source

def sourceSplit(source):
	"""sourceSplit(source) -> str, str, str
	
	Split the given source into it's parts.

	source must be of the form:
		nick!ident@host
	
	Example:
		nick, ident, host, = sourceSplit("Joe!Blogs@localhost")
	"""

	if "!" in source and "@" in source:
		nick, tmp = tuple(source.strip().split("!"))
		ident, host = tmp.split("@")
		return (nick, ident, host)
	else:
		return source

###
### Evenets
###

class RawEvent(Event):

	def __init__(self, data):
		Event.__init__(self,
				data=data)
	
class NumericEvent(Event):

	def __init__(self, source, target, numeric, arg, message):
		Event.__init__(self,
				source, target, numeric, arg, message)

class NetInfoEvent(Event):

	def __init__(self, gcount, ctime, protocol, key, x, y, z,
			network):
		Event.__init__(self, gcount, ctime, protocol, key,
				x, y, z, network)

class NewNickEvent(Event):

	def __init__(self, nick, hops, signon, ident, host,
			server, name):
		Event.__init__(self, nick, hops, signon, ident, host,
				server, name)

class NickEvent(Event):

	def __init__(self, nick, newNick, ctime):
		Event.__init__(self, nick, newNick, ctime)

class QuitEvent(Event):

	def __init__(self, nick, message):
		Event.__init__(self, nick, message)

class MessageEvent(Event):

	def __init__(self, source, target, message):
		Event.__init__(self, source, target, message)

class NoticeEvent(Event):

	def __init__(self, source, target, message):
		Event.__init__(self, source, target, message)

class PingEvent(Event):

	def __init__(self, server):
		Event.__init__(self, server)

class JoinEvent(Event):

	def __init__(self, nick, channel):
		Event.__init__(self, nick, channel)

class PartEvent(Event):

	def __init__(self, nick, channel, message):
		Event.__init__(self, nick, channel, message)

class CtcpEvent(Event):

	def __init__(self, source, target, ctcpType, message):
		Event.__init__(self, source, target, ctcpType, message)

class ModeEvent(Event):

	def __init__(self, nick, modes):
		Event.__init__(self, nick, modes)

class TopicEvent(Event):

	def __init__(self, channel, whoset, whenset, topic):
		Event.__init__(self, channel, whoset, whenset, topic)

class InviteEvent(Event):

	def __init__(self, source, target, channel):
		Event.__init__(self, source, target, channel)

class KickEvent(Event):

	def __init__(self, source, channel, target, message):
		Event.__init__(self, source, channel, target, message)

class MotdEvent(Event):

	def __init__(self, source, server):
		Event.__init__(self, source, server)

###
### Protocol Class
###

class IRC(Component):
	"""IRC(event) -> new irc object

	Create a new irc object which implements the IRC
	protocol. Note this doesn't actually do anything
	usefull unless used in conjunction with either
	pymills.sockets.TCPClient or pymills.sockets.TCPServer

	Sub-classes that wish to do something usefull with
	events that are processed and generated by the "READ"
	event must have filters/listeners associated with
	them. For instance, to do something with Message Events
	or PRIVMSG Events:

	{{{
	#!python
	class Client(IRC):

	   @listener("message")
	   def onMESSAGE(self, source, target, message):
	      print "Message from %s to %s" % (source, target)
	      print message
	}}}

	The available events that are processed and generated
	are pushed onto channels associated with that event.
	They are:
	 * numeric
	 * ctcp
	 * message
	 * notice
	 * join
	 * part
	 * nick
	 * ping
	 * newnick
	"""

	def __init__(self, *args):
		"initializes x; see x.__class__.__doc__ for signature"

		self.info = {}

	###
	### Properties
	###

	def getNick(self):
		"""I.getNick() -> str

		Return the current nickname if set,
		return None otherwise.
		"""

		return self.info.get("nick", None)

	def setNick(self, nick):
		"""I.setNick(nick) -> None

		Set the current nickname to the specified nickname.
		"""

		self.info["nick"] = nick.lower()

	def getIdent(self):
		"""I.getIdent() -> str

		Return the current ident if set,
		return None otherwise.
		"""

		return self.info.get("ident", None)

	def setIdent(self, ident):
		"""I.setIdent(ident) -> None

		Set the current ident to the specified ident.
		"""

		self.info["ident"] = ident.lower()

	def getHost(self):
		"""I.getHost() -> str

		Return the current host if set,
		return None otherwise.
		"""

		return self.info.get("host", None)

	def setHost(self, host):
		"""I.setHost(ident) -> None

		Set the current host to the specified host.
		"""

		self.info["host"] = host.lower()

	def getServer(self):
		"""I.getServer() -> str

		Return the current server if set,
		return None otherwise.
		"""

		return self.info.get("server", None)

	def setServer(self, server):
		"""I.setServer(ident) -> None

		Set the current server to the specified server.
		"""

		self.info["server"] = server.lower()

	def getName(self):
		"""I.getName() -> str

		Return the current name if set,
		return None otherwise.
		"""

		return self.info.get("name", None)

	def setName(self, name):
		"""I.setName(ident) -> None

		Set the current name to the specified server.
		"""

		self.info["name"] = name
	
	###
	### IRC Commands
	###

	def ircRAW(self, data):
		"""I.ircRAW(data) -> None
		
		Send a raw message

		This must be overridden by sub-classes in order to
		actually do anything usefull. By default it just
		pushes a RawEvent with the given data.
		"""

		self.event.push(RawEvent(data), "raw", self)
	
	def ircPASS(self, password):
		self.ircRAW("PASS %s" % password)

	def ircSERVER(self, server, hops, token, description):
		 self.ircRAW("SERVER %s %s %s :%s" % (server, hops,
			 token, description))
	
	def ircUSER(self, ident, host, server, name):
		self.ircRAW("USER %s \"%s\" \"%s\" :%s" % (
			ident, host, server, name))
		self.setIdent(ident)
		self.setHost(host)
		self.setServer(server)
		self.setName(name)
	
	def ircNICK(self, nick, idle=None, signon=None, ident=None,
			host=None, server=None, hops=None, name=None):

		if reduce(lambda x, y: x is not None and y is not None, [
			idle, signon, ident, host, server, hops, name]):

			self.ircRAW("NICK %s %d %d %s %s %s %d :%s" % (
				nick, idle, signon, ident, host, server,
				hops, name))

		else:
			self.ircRAW("NICK %s" % nick)
			self.setNick(nick)
	
	def ircPING(self, server):
		self.ircRAW("PING :%s" % server)

	def ircPONG(self, server):
		self.ircRAW("PONG :%s" % server) 

	def ircQUIT(self, message="", source=None):
		if source is None:
			self.ircRAW("QUIT :%s" % message)
		else:
			self.ircRAW(":%s QUIT :%s" % (source, message))
	
	def ircJOIN(self, channel, key=None, source=None):
		if source is None:
			if key is None:
				self.ircRAW("JOIN %s" % channel)
			else:
				self.ircRAW("JOIN %s %s" % (channel, key))
		else:
			if key is None:
				self.ircRAW(":%s JOIN %s" % (source, channel))
			else:
				self.ircRAW(":%s JOIN %s %s" % (source,
					channel, key))
	
	def ircPART(self, channel, message="", source=None):
		if source is None:
			self.ircRAW("PART %s :%s" % (channel, message))
		else:
			self.ircRAW(":%s PART %s :%s" % (source, channel,
				message))
	
	def ircPRIVMSG(self, target, message, source=None):
		if source is None:
			self.ircRAW("PRIVMSG %s :%s" % (target, message))
		else:
			self.ircRAW(":%s PRIVMSG %s :%s" % (source,
				target, message))

	def ircNOTICE(self, target, message, source=None):
		if source is None:
			self.ircRAW("NOTICE %s :%s" % (target, message))
		else:
			self.ircRAW(":%s NOTICE %s :%s" % (source,
				target, message))
	
	def ircCTCP(self, target, type, message, source=None):
		self.ircPRIVMSG(target, "%s %s" % (type, message),
				source)

	def ircCTCPREPLY(self, target, type, message, source=None):
		self.ircNOTICE(target, "%s %s" % (type, message),
			  source)
	
	def ircKICK(self, channel, target, message="", source=None):
		if source is None:
			self.ircRAW("KICK %s %s :%s" % (channel, target,
				message))
		else:
			self.ircRAW(":%s KICK %s %s :%s" % (source, channel,
				target,	message))
	
	def ircTOPIC(self, channel, topic, whoset=None,
			whenset=None, source=None):
		if source is None:
			if whoset is None and whenset is None:
				self.ircRAW("TOPIC %s :%s" % (channel, topic))
			else:
				self.ircRAW("TOPIC %s %s %d :%s" % (channel,
					whoset, whenset, topic)),
		else:
			if whoset is None and whenset is None:
				self.ircRAW(":%s TOPIC %s :%s" % (source,
					channel, topic))
			else:
				self.ircRAW(":%s TOPIC %s %s %d :%s" % (source,
					channel, whoset, whenset, topic)),
	
	def ircMODE(self, modes, channel=None, source=None):
		if source is None:
			if channel is None:
				self.ircMODE("MODE :%s" % modes)
			else:
				self.ircMODE("MODE %s :%s" % (channel, modes))
		else:
			if channel is None:
				self.ircMODE(":%s MODE :%s" % (source, modes))
			else:
				self.ircMODE(":%s MODE %s :%s" % (source, channel,
					modes))
	
	def ircKILL(self, target, message):
		self.ircRAW("KILL %s :%s" % (target, message))
	
	def ircINVITE(self, target, channel, source=None):
		if source is None:
			self.ircRAW("INVITE %s %s" % (target, channel))
		else:
			self.ircRAW(":%s INVITE %s %s" % (source, target,
				channel))

	###
	### Event Processing
	###

	@listener("read")
	def onREAD(self, line):
		"""I.onREAD(line) -> None

		Process a line of text and generate the appropiate
		event. This must not be overridden by sub-classes,
		if it is, this must be explitetly called by the
		sub-class.
		"""

		tokens = line.split(" ")

		if tokens[0] == "PING":
			self.event.push(
					PingEvent(strip(tokens[1]).lower()),
					"ping", self)

		elif tokens[0] == "NICK":
			self.event.push(
					NewNickEvent(
						tokens[1].lower(), int(tokens[2]),
						int(tokens[3]), tokens[4].lower(),
						tokens[5].lower(), tokens[6].lower(),
						strip(" ".join(tokens[8:]))),
					"newnick", self)

		elif tokens[0] == "TOPIC":
			self.event.push(
					TopicEvent(
						tokens[1], tokens[2], int(tokens[3]),
						strip(" ".join(tokens[4:]))),
					"topic", self)

		elif tokens[0] == "NETINFO":
			self.event.push(
					NetInfoEvent(
						int(tokens[1]),
						int(tokens[2]),
						tokens[3],
						tokens[4],
						tokens[5],
						tokens[6],
						tokens[7],
						strip(" ".join(tokens[8:]))),
					"netinfo", self)

		elif re.match("[0-9]+", tokens[1]):
			source = sourceSplit(strip(tokens[0].lower()))
			target = tokens[2].lower()

			numeric = int(tokens[1])
			if tokens[3][0] == ":":
				arg = None
				message = strip(" ".join(tokens[3:]))
			else:
				arg = tokens[3]
				message = strip(" ".join(tokens[4:]))

			self.event.push(
					NumericEvent(source, target, numeric,
						arg, message),
					"numeric", self)

		elif tokens[1] == "PRIVMSG":
			source = sourceSplit(strip(tokens[0].lower()))
			target = tokens[2].lower()
			message = strip(" ".join(tokens[3:]))

			if not message == "":
				if message[0] == "":
					tokens = strip(message, color=True).split(" ")
					type = tokens[0].lower()
					message = " ".join(tokens[1:])
					self.event.push(
							CtcpEvent(source, target, type, message),
							"ctcp", self)
				else:
					self.event.push(
							MessageEvent(source, target, message),
							"message", self)
			else:
				self.event.push(
						MessageEvent(source, target, message),
						"message", self)

		elif tokens[1] == "NOTICE":
			source = sourceSplit(strip(tokens[0].lower()))
			target = tokens[2].lower()
			message = strip(" ".join(tokens[3:]))
			self.event.push(
					NoticeEvent(source, target, message),
					"notice", self)

		elif tokens[1] == "JOIN":
			source = sourceSplit(strip(tokens[0].lower()))
			channels = strip(tokens[2]).lower()
			for channel in channels.split(","):
				self.event.push(
						JoinEvent(source, channel),
						"join", self)

		elif tokens[1] == "PART":
			source = sourceSplit(strip(tokens[0].lower()))
			channel = strip(tokens[2]).lower()
			message = strip(" ".join(tokens[3:]))
			self.event.push(
					PartEvent(source, channel, message),
					"part", self)

		elif tokens[1] == "QUIT":
			source = sourceSplit(strip(tokens[0].lower()))
			message = strip(" ".join(tokens[2:]))
			self.event.push(
					QuitEvent(source, message),
					"quit", self)

		elif tokens[1] == "NICK":
			source = sourceSplit(strip(tokens[0].lower()))
			newNick = strip(tokens[2]).lower()
			if len(tokens) == 4:
				ctime = strip(tokens[3])
			else:
				ctime = time.time()
			self.event.push(
					NickEvent(source, newNick, ctime),
					"nick", self)

		elif tokens[1] == "MOTD":
			source = sourceSplit(strip(tokens[0].lower()))
			server = strip(tokens[2]).lower()
			self.event.push(
					MotdEvent(source, server),
					"motd", self)

	###
	### Default Events
	###

	@listener("ping")
	def onPING(self, server):
		"""Ping Event

		This is a default event ro respond to Ping Events
		by sending out a Pong in response. Sub-classes
		may override this, but be sure to respond to
		Ping Events by either explitetly calling this method
		or sending your own Pong reponse.
		"""

		self.ircPONG(server)

###
### Errors and Numeric Replies
###

RPL_TRACELINK = 200
RPL_TRACECONNECTING = 201
RPL_TRACEHANDSHAKE = 202
RPL_TRACEUNKNOWN = 203
RPL_TRACEOPERATOR = 204
RPL_TRACEUSER = 205
RPL_TRACESERVER = 206
RPL_TRACENEWTYPE = 208
RPL_TRACELOG = 261
RPL_STATSLINKINFO = 211
RPL_STATSCOMMANDS = 212
RPL_STATSCLINE = 213
RPL_STATSNLINE = 214
RPL_STATSILINE = 215
RPL_STATSKLINE = 216
RPL_STATSYLINE = 218
RPL_ENDOFSTATS = 219
RPL_STATSLLINE = 241
RPL_STATSUPTIME = 242
RPL_STATSOLINE = 243
RPL_STATSHLINE = 244
RPL_UMODEIS = 221
RPL_LUSERCLIENT = 251
RPL_LUSEROP = 252
RPL_LUSERUNKNOWN = 253
RPL_LUSERCHANNELS = 254
RPL_LUSERME = 255
RPL_ADMINME = 256
RPL_ADMINLOC1 = 257
RPL_ADMINLOC2 = 258
RPL_ADMINEMAIL = 259

RPL_NONE = 300
RPL_USERHOST = 302
RPL_ISON = 303
RPL_AWAY = 301
RPL_UNAWAY = 305
RPL_NOWAWAY = 306
RPL_WHOISUSER = 311
RPL_WHOISSERVER = 312
RPL_WHOISOPERATOR = 313
RPL_WHOISIDLE = 317
RPL_ENDOFWHOIS = 318
RPL_WHOISCHANNELS = 319
RPL_WHOWASUSER = 314
RPL_ENDOFWHOWAS = 369
RPL_LIST = 322
RPL_LISTEND = 323
RPL_CHANNELMODEIS = 324
RPL_NOTOPIC = 331
RPL_TOPIC = 332
RPL_INVITING = 341
RPL_SUMMONING = 342
RPL_VERSION = 351
RPL_WHOREPLY = 352
RPL_ENDOFWHO = 315
RPL_NAMREPLY = 353
RPL_ENDOFNAMES = 366
RPL_LINKS = 364
RPL_ENDOFLINKS = 365
RPL_BANLIST = 367
RPL_ENDOFBANLIST = 368
RPL_INFO = 371
RPL_ENDOFINFO = 374
RPL_MOTDSTART = 375
RPL_MOTD = 372
RPL_ENDOFMOTD = 376
RPL_YOUREOPER = 381
RPL_REHASHING = 382
RPL_TIME = 391
RPL_USERSSTART = 392
RPL_USERS = 393
RPL_ENDOFUSERS = 394
RPL_NOUSERS = 395

ERR_NOSUCHNICK = 401
ERR_NOSUCHSERVER = 402
ERR_NOSUCHCHANNEL = 403
ERR_CANNOTSENDTOCHAN = 404
ERR_TOOMANYCHANNELS = 405
ERR_WASNOSUCHNICK = 406
ERR_TOOMANYTARGETS = 407
ERR_NOORIGIN = 409
ERR_NORECIPIENT = 411
ERR_NOTEXTTOSEND = 412
ERR_NOTOPLEVEL = 413
ERR_WILDTOPLEVEL = 414
ERR_UNKNOWNCOMMAND = 421
ERR_NOMOTD = 422
ERR_NOADMININFO = 423
ERR_FILEERROR = 424
ERR_NONICKNAMEGIVEN = 431
ERR_ERRONEUSNICKNAME = 432
ERR_NICKNAMEINUSE = 433
ERR_NICKCOLLISION = 436
ERR_NOTONCHANNEL = 442
ERR_USERONCHANNEL = 443
ERR_NOLOGIN = 444
ERR_SUMMONDISABLED = 445
ERR_USERSDISABLED = 446
ERR_NOTREGISTERED = 451
ERR_NEEDMOREPARAMS = 461
ERR_ALREADYREGISTRED = 462
ERR_PASSWDMISMATCH = 464
ERR_YOUREBANNEDCREEP = 465
ERR_KEYSET = 467
ERR_CHANNELISFULL = 471
ERR_UNKNOWNMODE = 472
ERR_INVITEONLYCHAN = 473
ERR_BANNEDFROMCHAN = 474
ERR_BADCHANNELKEY = 475
ERR_NOPRIVILEGES = 481
ERR_CHANOPRIVSNEEDED = 482
ERR_CANTKILLSERVER = 483
ERR_NOOPERHOST = 491

ERR_UMODEUNKNOWNFLAG = 501
ERR_USERSDONTMATCH = 502
