# Filename: irc.py
# Module:	irc
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Internet Relay Chat

This is a Internet Relay Chat module containing classes that
aid in the creation of IRC clients and servers.
Simply write your program as an extension of one or more of
these classes.
"""

from utils import Tokenizer
from sockets import TCPClient

# Supporting Functions

def strip(s, color=False):
	s = s.lstrip(":")
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
	
class Server(TCPClient):

	def __init__(self):
		TCPClient.__init__(self)
	
	def __del__(self):
		if self.connected: self.ircQUIT("")

	# IRC Commands

	def ircRAW(self, data):
		self.write("%s\r\n" % data)
	
	def ircPASS(self, password):
		self.ircRAW("PASS %s" % password)
	
	def ircSERVER(self, server, hops, token, description):
		self.ircRAW("SERVER %s %s %s :%s" %
				(server, hops, token, description))
	
	def ircNICK(self, nick, idle, signon, ident, host, server,
			hops, name):
		self.ircRAW("NICK %s %d %d %s %s %s %d :%s" %
				(nick, idle, signon, ident, host, server,
					hops, name))
	
	def ircQUIT(self, nick=None, message=""):
		if nick is not None:
			self.ircRAW(":%s QUIT :%s" % (nick, message))
		else:
			self.ircRAW("QUIT :%s" % message)
	
	def ircPONG(self, daemon):
		self.ircRAW("PONG %s" % daemon)
	
	def ircPRIVMSG(self, source, target, message):
		self.ircRAW(":%s PRIVMSG %s :%s" % (
			source, target, message))

	def ircNOTICE(self, source, target, message):
		self.ircRAW(":%s NOTICE %s :%s" % (
			source, target, message))
	
	def ircJOIN(self, nick, channel):
		self.ircRAW(":%s JOIN %s" % (nick, channel))

	def ircPART(self, nick, channel):
		self.ircRAW(":%s PART %s" % (nick, channel))
	
	def ircMODE(self, source, target, modes):
		self.ircRAW(":%s MODE %s %s" % (source, target, modes))
	
	def ircKICK(self, source, channel, target, message):
		self.ircRAW(":%s KICK %s %s :%s" % (
			source, channel, target, message))
	
	def ircINVITE(self, source, target, channel):
		self.ircRAW(":%s INVITE %s %s" % (
			source, target, channel))
	
	def ircTOPIC(self, nick, channel, topic, whoset=None, whenset=None):
		if whoset is None and whenset is None:
			self.ircRAW(":%s TOPIC %s :%s" % (
				nick, channel, topic))
		else:
			self.ircRAW(":%s TOPIC %s %s %d :%s" % (
				nick, channel, whoset, whenset, topic))

	def ircCTCP(self, source, target, type, message):
		self.ircPRIVMSG(source, target, "%s %s" % (type, message))

	def ircCTCPREPLY(self, source, target, type, message):
		self.ircNOTICE(source, target, "%s %s" % (type, message))

	# IRC Event Handler
	
	def onREAD(self, line):
		self.onRAW(line)
		
	def onRAW(self, data):
		tokens = Tokenizer(data)

		if tokens[1] == "PRIVMSG":
			source = sourceSplit(strip(tokens[0]))
			target = tokens[2]
			message = strip(tokens.copy(3))

			if not message == "":
				if message[0] == "":
					tokens = Tokenizer(message[1:len(message)])
					type = tokens.next()
					message = tokens.next()
					self.onCTCP(source, target, type, message)
				else:
					self.onMESSAGE(source, target, message)
			else:
				self.onMESSAGE(source, target, message)

		elif tokens[1] == "NOTICE":
			source = sourceSplit(strip(tokens[0]))
			target = tokens[2]
			message = strip(tokens.copy(3))
			self.onNOTICE(source, target, message)
		elif tokens[1] == "JOIN":
			source = sourceSplit(strip(tokens[0]))
			channel = strip(tokens[2])
			self.onJOIN(source, channel)
		elif tokens[1] == "PART":
			source = sourceSplit(strip(tokens[0]))
			channel = strip(tokens[2])
			message = strip(tokens.copy(3))
			self.onPART(source, channel, message)
		elif tokens[1] == "QUIT":
			source = sourceSplit(strip(tokens[0]))
			message = strip(tokens.copy(2))
			self.onQUIT(source, message)
		elif tokens[1] == "NICK":
			source = sourceSplit(strip(tokens[0]))
			newnick = strip(tokens[2])
			ctime = strip(tokens[3])
			self.onNICK(source, newnick, ctime)
		elif tokens[1] == "TOPIC":
			source = sourceSplit(strip(tokens[0]))
			channel, whoset, whenset = tokens[2:5]
			topic = strip(tokens.copy(5))
			self.onTOPIC(channel, whoset, whenset, topic)
		elif tokens[0] == "PING":
			server = strip(tokens[1])
			self.onPING(server)
		elif tokens[0] == "NICK":
			del tokens[0]
			self.onNEWNICK(*tokens)
		elif tokens[0] == "TOPIC":
			del tokens[0]
			channel, whoset, whenset = tokens[:3]
			topic = strip(tokens.copy(3))
			self.onTOPIC(channel, whoset, whenset, topic)
	
	# IRC Events
	
	def onNEWNICK(self, nick, hops, signon, ident, host,
			server, unused, *name):
		pass
	
	def onNICK(self, source, newnick, ctime):
		pass
	
	def onQUIT(self, nick, message):
		pass
	
	def onMESSAGE(self, source, target, message):
		pass
	
	def onNOTICE(self, source, target, message):
		pass
	
	def onPING(self, server):
		self.ircPONG(server)
	
	def onJOIN(self, source, channel):
		pass

	def onPART(self, source, channel, message):
		pass

	def onCTCP(self, source, target, type, message):
		pass
	
	def onTOPIC(self, channel, whoset, whenset, topic):
		pass
	
class Client(TCPClient):

	def __init__(self):
		TCPClient.__init__(self)
		self.me = {}
	
	def __del__(self):
		if self.connected: self.ircQUIT("")

	def getNick(self):
		return self.me["nick"]

	# IRC Commands

	def ircRAW(self, data):
		self.write("%s\r\n" % data)
	
	def ircSERVER(self, host, port, password = None):
		self.open(host, port)
	
	def ircQUIT(self, message = ''):
		self.ircRAW('QUIT :' + message)
		self.close()
		self.connected = False
	
	def ircUSER(self, user, host, server, name):
		self.ircRAW("USER %s \"%s\" \"%s\" :%s" % (
			user, host, server, name))
		self.me["user"] = user
		self.me["host"] = host
		self.me["server"] = server
		self.me["name"] = name
	
	def ircNICK(self, nick):
		self.ircRAW("NICK %s" % nick)
		self.me["nick"] = nick
	
	def ircPING(self, server):
		self.ircRAW("PING :%s" % server)

	def ircPONG(self, daemon):
		self.ircRAW("PONG :%s" % daemon)
	
	def ircJOIN(self, channel, key = None):
		if key is None:
			self.ircRAW('JOIN ' + channel)
		else:
			self.ircRAW('JOIN ' + channel + ' ' + key)
	
	def ircPART(self, channel, message = 'Leaving...'):
		self.ircRAW('PART ' + channel + ' :' + message)
	
	def ircPRIVMSG(self, to, message):
		self.ircRAW("PRIVMSG %s :%s" % (to, message))

	def ircNOTICE(self, to, message):
		self.ircRAW("NOTICE %s :%s" % (to, message))
	
	def ircCTCP(self, to, type, message):
		self.ircPRIVMSG(to, '' + type + " " + message)

	def ircCTCPREPLY(self, to, type, message):
		self.ircNOTICE(to, '' + type + " " + message)
	
	def ircKICK(self, channel, nick, message):
		self.ircRAW("KICK %s %s :%s" % (channel, nick, message))
	
	def ircTOPIC(self, channel, topic):
		self.ircRAW('TOPIC ' + channel + ' :' + topic)
	
	def ircMODE(self, channel, nick, mode):
		self.ircRAW('MODE ' + channel + ' ' + mode + ' ' + nick)
	
	def ircMODE(self, mode):
		self.ircMODE('MODE ' + mode)
	
	def ircOP(self, channel, nick):
		self.MODE(channel, nick, '+o')

	def ircDEOP(self, channel, nick):
		self.MODE(channel, nick, '-o')

	def ircVOICE(self, channel, nick):
		self.MODE(channel, nick, '+v')

	def ircDEVOICE(self, channel, nick):
		self.MODE(channel, nick, '-v')

	# IRC Event Handler
	
	def onREAD(self, line):
		self.onRAW(line)
		
	def onRAW(self, data):
		tokens = Tokenizer(data)

		if tokens[1] == 'PRIVMSG':
			source = sourceSplit(strip(tokens[0]))
			target = tokens[2]
			message = strip(tokens.copy(3))

			if not message == '':
				if message[0] == '':
					tokens = Tokenizer(message[1:len(message)])
					type = tokens.next()
					message = tokens.next()
					self.onCTCP(source, target, type, message)
				else:
					self.onMESSAGE(source, target, message)
			else:
				self.onMESSAGE(source, target, message)

		elif tokens[1] == 'NOTICE':
			source = sourceSplit(strip(tokens[0]))
			target = tokens[2]
			message = strip(tokens.copy(3))
			self.onNOTICE(source, target, message)
		elif tokens[1] == 'JOIN':
			source = sourceSplit(strip(tokens[0]))
			channel = strip(tokens[2])
			self.onJOIN(source, channel)
		elif tokens[1] == 'PART':
			source = sourceSplit(strip(tokens[0]))
			channel = strip(tokens[2])
			message = strip(tokens.copy(3))
			self.onPART(source, channel, message)
		elif tokens[0] == 'PING':
			server = strip(tokens[1])
			self.onPING(server)
	
	# IRC Events
	
	def onMESSAGE(self, source, target, message):
		pass
	
	def onNOTICE(self, source, target, message):
		pass
	
	def onPING(self, server):
		self.ircPING(server)
	
	def onJOIN(self, source, channel):
		pass

	def onPART(self, source, channel, message):
		pass
	
	def onCTCP(self, source, target, type, message):
		pass
	
	def onNICK(self, source, nick):
		pass
	
	def onMODE(self, nick, modes):
		pass
	
	def onMODE(self, source, channel, modes):
		pass
	
	def onQUIT(self, nick, reason):
		pass
	
	def onTOPIC(self, nick, channel, topic):
		pass
	
	def onINVITE(self, source, to, channel):
		pass
	
	def onKICK(self, source, channel, nick, reason):
		pass
