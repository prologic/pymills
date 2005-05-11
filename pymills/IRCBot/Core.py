# Filename: Core.py
# Module:   Core
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Core

Core module of IRCBot
"""

import sys, traceback, signal, os
import IRC
import Timers

class Bot(IRC.Client):
	"""Bot

	Main Bot Class
	"""

	def __init__(self):
		IRC.Client.__init__(self)

		self.timers = Timers.Timers()
		self.plugins = []

		if os.name == "posix" or os.name == "mac":
			signal.signal(signal.SIGHUP, self.rehash)
			signal.signal(signal.SIGTERM, self.term)

	# Service Commands

	def term(self, signal = 0, stack = 0):
		self.stop()
		sys.exit(0)
	
	def stop(self):
		self.ircQUIT()
	
	def rehash(self):
		pass # Implemented by sub-classes
	
	# Plugin Support

	def loadedPlugins(self):
		plugins = []
		for plugin in self.plugins:
			plugins.append(plugin.__class__.__name__)
		return plugins

	def getPluginInfo(self, path, plugin):
		if not path in sys.path:
			sys.path.append(path)
		available_plugins = self.getPlugins(path)
		info = {}
		if plugin in available_plugins:
			module = __import__(plugin)
			info["name"] = module.__name__
			info["ver"] = module.__ver__
			info["author"] = module.__author__
			info["desc"] = module.__desc__
		return info

	def getPlugin(self, plugin):
		for tmp in self.plugins:
			if tmp.__class__.__name__.lower() == plugin.lower():
				return tmp
		return None

	def getPlugins(self, path):
		plugins = []
		for file in os.listdir(path):
			(root, ext) = os.path.splitext(file)
			if ext == ".py":
				plugins.append(root)
		return plugins

	def loadPlugins(self, path, plugins):
		print "Plugin path: %s" % path
		print "Plugin list: %s" % repr(plugins)
		if not path in sys.path:
			sys.path.append(path)
		available_plugins = self.getPlugins(path)
		print "Available Plugins: %s" % repr(available_plugins)
		for plugin in plugins:
			if plugin in available_plugins:
				module = __import__(plugin)
				if hasattr(module, "init") and callable(getattr(module, "init")):
					getattr(module, "init")()
				if hasattr(module, plugin) and callable(getattr(module, plugin)):
					self.addPlugin(getattr(module, plugin))
	
	def addPlugin(self, plugin):
		self.plugins.append(plugin(self))
	
	# High Level Commands

	def joinChannels(self, channels):
		for channel in channels:
			self.ircJOIN(channel)
	
	# Main Event Handler

	def handleEvent(self, type, *args):
		print "Event: %s" % type
		print repr(args)
		for plugin in self.plugins:
			method = "on%s" % type
			print "method: %s" % method
			if hasattr(plugin, method) and callable(getattr(plugin, method)):
				getattr(plugin, method)(*args)
	
	# Run

	def run(self):
		while self.connected:
			self.process()
			self.timers.run()

	# IRC Evenets

	def onMESSAGE(self, source, target, message):
		self.handleEvent("MESSAGE", source, target, message)
	
	def onNOTICE(self, source, target, message):
		self.handleEvent("NOTICE", source, target, message)
	
	def onPING(self, server):
		IRC.Client.onPING(self, server)
		self.handleEvent("PING", server)
	
	def onJOIN(self, source, channel):
		self.handleEvent("JOIN", source, channel)

	def onPART(self, source, channel, message):
		self.handleEvent("PART", source, channel)
	
	def onCTCP(self, source, target, type, message):
		self.handleEvent("CTCP", source, target, type, message)
	
	def onNICK(self, source, nick):
		self.handleEvent("NICK", source, nick)
	
	def onMODE(self, nick, modes):
		self.handleEvent("MODE", nick, modes)
	
	def onMODE(self, source, channel, modes):
		self.handleEvent("MODE", source, channel, modes)
	
	def onQUIT(self, nick, reason):
		self.handleEvent("QUIT", nick, reason)
	
	def onTOPIC(self, nick, channel, topic):
		self.handleEvent("TOPIC", nick, channel, topic)
	
	def onINVITE(self, source, to, channel):
		self.handleEvent("INVITE", source, to, channel)
	
	def onKICK(self, source, channel, nick, reason):
		self.handleEvent("KICK", source, channel, nick, reason)

class Plugin:

	def __init__(self, bot):
		self.bot = bot
	
	def isAddressed(self, source, target, message):
		addressed = False

		if target.lower() == self.bot.getNick().lower():
			addressed = True
			target = source[0]
		else:
			if len(message) > len(self.bot.getNick()):
				if message[0:len(self.bot.getNick())] == self.bot.getNick():
					addressed = True
					i = len(self.bot.getNick()) + 1
					if not i == len(message):
						while message[i] in [':', ',', ' ']:
							i = i + 1
							if i == len(message):
								break
					message = message[i:len(message)]

		return (addressed, target, message)
