# Filename: irc.py
# Module:	irc
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Internet Relay Chat

This is a Internet Relay Chat module containing classes that
aid in the creation of IRC clients and servers.
"""

from event import Event

__all__ = [
		"strip", "sourceJoin", "sourceSplit",
		"IRCClient",
		"RawEvent"
		]

# Supporting Functions

def strip(s, color=False):
	if len(s) > 0:
		if s[0] == ":":
			s = s[1:]
	if color:
		s = s.replace("\x01", "")
		s = s.replace("\x02", "")
	return s
	
def sourceJoin(source):
	return "%s!%s@%s" % source

def sourceSplit(source):
	"""Split the given source into it's parts.

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

class RawEvent(Event):

	def __init__(self, data):
		Event.__init__(self, type="raw", data=data)
	
class NewNickEvent(Event):

	def __init__(self, nick, hops, signon, ident, host,
			server, name):
		Event.__init__(self, type="newnick", nick=nick,
				hops=hops, signon=signon, ident=ident,
				host=host, server=server, name=name)

class NickEvent(Event):

	def __init__(self, nick, newNick, ctime):
		Event.__init__(self, type="nick", nick=nick,
				newNick=newNick, ctime=ctime)

class QuitEvent(Event):

	def __init__(self, nick, message):
		Event.__init__(self, type="quit", nick=nick,
				message=message)

class MessageEvent(Event):

	def __init__(self, source, target, message):
		Event.__init__(self, type="message", source=source,
				target=target, message=message)

class NoticeEvent(Event):

	def __init__(self, source, target, message):
		Event.__init__(self, type="notice", source=source,
				target=target, message=message)

class PingEvent(Event):

	def __init__(self, server):
		Event.__init__(self, type="ping", server=server)

class JoinEvent(Event):

	def __init__(self, nick, channel):
		Event.__init__(self, type="join", nick=nick,
				channel=channel)

class PartEvent(Event):

	def __init__(self, nick, channel, message):
		Event.__init__(self, type="part", nick=nick,
				channel=channel, message=message)

class CtcpEvent(Event):

	def __init__(self, source, target, ctcpType, message):
		Event.__init__(self, type="ctcp", source=source,
				target=target, ctcpType=ctcpType, message=message)

class ModeEvent(Event):

	def __init__(self, nick, modes):
		Event.__init__(self, type="mode", nick=nick,
				modes=modes)

class TopicEvent(Event):

	def __init__(self, nick, channel, topic, whoset=None,
			whenset=None):
		Event.__init__(self, type="topic", nick=nick,
				channel=channel, topic=topic, whoset=whoset,
				whenset=whenset)

class InviteEvent(Event):

	def __init__(self, source, target, channel):
		Event.__init__(self, type="invite", source=source,
				target=target, channel=channel)

class KickEvent(Event):

	def __init__(self, source, channel, target, message):
		Event.__init__(self, type="kick", source=source,
				channel=channel, target=target, message=message)

class WriteEvent(Event):

	def __init__(self, data):
		Event.__init__(self, type="write", data=data)

class IRC:

	def __init__(self, event):
		self.event = event
		self.info = {}

		self.__setupEvents__()

	def __del__(self):
		if self.connected:
			self.ircQUIT()

	def __setupEvents__(self):
		import inspect

		events = [(x[0][2:].lower(), x[1]) 
				for x in inspect.getmembers(
					self, lambda x: inspect.ismethod(x) and \
					callable(x) and x.__name__[:2] == "on")]

		for event, handler in events:
			channel = self.event.getChannelID(event)
			if channel is None:
				self.event.addChannel(event)
				channel = self.event.getChannelID(event)
			if getattr(handler, "filter", False):
				self.event.addFilter(handler,
						self.event.getChannelID(event))
			else:
				self.event.addListener(handler,
						self.event.getChannelID(event))

	def getNick(self):
		return self.info.get("nick", None)

	def setNick(self, nick):
		self.info["nick"] = nick.lower()

	def getIdent(self):
		return self.info.get("ident", None)

	def setIdent(self, ident):
		self.info["ident"] = ident.lower()

	def getHost(self):
		return self.info.get("host", None)

	def setHost(self, host):
		self.info["host"] = host.lower()

	def getServer(self):
		return self.info.get("server", None)

	def setServer(self, server):
		self.info["server"] = server.lower()

	def getName(self):
		return self.info.get("name", None)

	def setName(self, name):
		self.info["name"] = name
	
	nick = property(getNick, setNick)
	user = property(getIdent, setIdent)
	host = property(getHost, setHost)
	server = property(getServer, setServer)
	name = property(getName, setName)

	def ircRAW(self, data):
		self.event.push(WriteEvent(data + "\r\n"),
				self.event.getChannelID("write"),
				self)
	
	def ircPASS(self, password):
		self.ircRAW("PASS %s" % password)

	def ircSERVER(self, server, hops, token, description):
		 self.ircRAW("SERVER %s %s %s :%s" % (server, hops,
			 token, description))
	
	def ircUSER(self, user, host, server, name):
		self.ircRAW("USER %s \"%s\" \"%s\" :%s" % (
			user, host, server, name))
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
			self.close()
			self.connected = False
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
		self.ircPRIVMSG(target, "%s %s" % (type, message),
				source)

	def ircCTCPREPLY(self, target, type, message, source=None):
		self.ircNOTICE(target, "%s %s" % (type, message),
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

	def onREAD(self, event):
		tokens = event.line.split(" ")

		#TODO: Add TOPIC

		if tokens[1] == "PRIVMSG":
			source = sourceSplit(strip(tokens[0])).lower()
			target = tokens[2].lower()
			message = strip(" ".join(tokens[3:]))

			if not message == "":
				if message[0] == "":
					tokens = strip(message, color=True).split(" ")
					type = tokens[0].lower()
					message = " ".join(tokens[1:])
					self.event.push(
							CtcpEvent(source, target, type, message),
							self.event.getChannelID("ctcp"),
							self)
				else:
					self.event.push(
							MessageEvent(source, target, message),
							self.event.getChannelID("message"),
							self)
			else:
				self.event.push(
						MessageEvent(source, target, message),
						self.event.getChannelID("message"),
						self)

		elif tokens[1] == "NOTICE":
			source = sourceSplit(strip(tokens[0])).lower()
			target = tokens[2].lower()
			message = strip(" ".join(tokens[3:]))
			self.event.push(
					NoticeEvent(source, target, message),
					self.event.getChannelID("notice"),
					self)

		elif tokens[1] == "JOIN":
			source = sourceSplit(strip(tokens[0])).lower()
			channel = strip(tokens[2]).lower()
			self.event.push(
					JoinEvent(source, channel),
					self.event.getChannelID("join"),
					self)

		elif tokens[1] == "PART":
			source = sourceSplit(strip(tokens[0])).lower()
			channel = strip(tokens[2]).lower()
			message = strip(" ".join(tokens[3:]))
			self.event.push(
					PartEvent(source, channel, message),
					self.event.getChannelID("part"),
					self)

		elif tokens[1] == "QUIT":
			source = sourceSplit(strip(tokens[0])).lower()
			message = strip(" ".join(tokens[2:]))
			self.event.push(
					QuitEvent(source, message),
					self.event.getChannelID("quit"),
					self)

		elif tokens[1] == "NICK":
			source = sourceSplit(strip(tokens[0])).lower()
			newNick = strip(tokens[2]).lower()
			ctime = strip(tokens[3])
			self.event.push(
					NickEvent(source, newNick, ctime),
					self.event.getChannelID("nick"),
					self)

		elif tokens[0] == "PING":
			self.event.push(
					PingEvent(strip(tokens[1]).lower()),
					self.event.getChannelID("ping"),
					self)

		elif tokens[0] == "NICK":
			self.event.push(
					NewNickEvent(
						tokens[1].lower(), int(tokens[2]),
						int(tokens[3]), tokens[4].lower(),
						tokens[5].lower(), tokens[6].lower(),
						strip(" ".join(tokens[8:]))),
					self.event.getChannelID("newnick"),
					self)

	def onPING(self, event):
		self.ircPONG(event.server)
