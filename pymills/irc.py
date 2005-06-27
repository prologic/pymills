# Filename: IRC.py
# Module:   IRC
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""IRC Module"""

import sys
import time
import string

from utils import Tokenizer
from sockets import TCPClient
from sockets import TCPServer

# Supporting Functions

def strip(s, color=False):
	s = s.lstrip(":")
	if color:
		s = s.replace("\x01", "")
		s = s.replace("\x02", "")
	return s
	
def parseSource(source):
	ex = string.find(source, '!')
	at = string.find(source, '@')

	nick = source[0:ex]
	user = source[(ex + 1):at]
	host = source[(at + 1):]

	return (nick, user, host)
	

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

		if tokens[1] == 'PRIVMSG':
			source = parseSource(strip(tokens[0]))
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
			source = parseSource(strip(tokens[0]))
			target = tokens[2]
			message = strip(tokens.copy(3))
			self.onNOTICE(source, target, message)
		elif tokens[1] == 'JOIN':
			source = parseSource(strip(tokens[0]))
			channel = strip(tokens[2])
			self.onJOIN(source, channel)
		elif tokens[1] == 'PART':
			source = parseSource(strip(tokens[0]))
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
