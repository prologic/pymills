# Filename: IRC.py
# Module:   IRC
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""IRC

IRC Library

* Client
* Server
"""

import sys, string, time
from Sockets import TCPClient, TCPServer
from Tokenizer import Tokenizer

#Supporting Functions

def _strip(str):
	if len(str) > 0:
		if str[0] == ':':
			return str[1:len(str)]
		return str
	else:
		return ''
	
def _parseSource(source):
	ex = string.find(source, '!')
	at = string.find(source, '@')

	nick = source[0:ex]
	user = source[(ex + 1):at]
	host = source[(at + 1):]

	return (nick, user, host)
	

class Client(TCPClient):

	def __init__(self):
		"Initialize Class"

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
		self.ircRAW("USER %s \"%s\" \"%s\" :%s" % (user, host, server, name))
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
		if message is None:
			self.ircRAW('KICK ' + channel + ' ' + nick)
		else:
			self.ircRAW('KICK ' + channel + ' ' + nick + ' :' + message)
	
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

		if tokens.tokens[1] == 'PRIVMSG':
			source = _parseSource(_strip(tokens.tokens[0]))
			target = tokens.tokens[2]
			tokens.delete(3)
			message = _strip(tokens.rest())

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

		elif tokens.tokens[1] == 'NOTICE':
			source = _parseSource(_strip(tokens.tokens[0]))
			target = tokens.tokens[2]
			tokens.delete(3)
			message = _strip(tokens.rest())
			self.onNOTICE(source, target, message)
		elif tokens.tokens[1] == 'JOIN':
			source = _parseSource(_strip(tokens.tokens[0]))
			channel = _strip(tokens.tokens[2])
			self.onJOIN(source, channel)
		elif tokens.tokens[1] == 'PART':
			source = _parseSource(_strip(tokens.tokens[0]))
			channel = _strip(tokens.tokens[2])
			tokens.delete(3)
			message = _strip(tokens.rest())
			self.onPART(source, channel, message)
		elif tokens.tokens[0] == 'PING':
			server = _strip(tokens.tokens[1])
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
	
# vim: tabstop=3 nocindent autoindent
