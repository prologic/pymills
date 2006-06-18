# Filename: env.py
# Module:	env
# Date:		10th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Environment Container

...
"""

import os

try:
	import default_config
except:
	default_config = None

VERSION = 1

class Environment:

	def __init__(self, path, name="PyMills",
			url="http://trac.shortcircuit.net.au/projects/pymills/",
			create=False):
		self.path = os.path.abspath(os.path.expanduser(path))

		if create:
			self.create()
		else:
			self.verify()

		self.loadConfig()
		self.setupLog()
		self.loadDB()

	def create(self):

		def createFile(filename, data=None):
			fd = open(filename, 'w')
			if data is not None:
				fd.write(data)
			fd.close()

		# Create the directory structure
		os.mkdir(self.path)
		os.mkdir(os.path.join(self.path, "db"))
		os.mkdir(os.path.join(self.path, "log"))
		os.mkdir(os.path.join(self.path, "conf"))
		os.mkdir(os.path.join(self.path, "help"))
		os.mkdir(os.path.join(self.path, "plugins"))
		os.mkdir(os.path.join(self.path, "services"))
		os.mkdir(os.path.join(self.path, "messages"))

		# Create a few files
		createFile(os.path.join(self.path, "VERSION"),
				"%s Environment Version %d\n" % (
					self.name, VERSION))
		createFile(os.path.join(self.path, "README"),
				"This directory contains a %s environment.\n"
				"Visit %s for more information.\n" % (
					self.name, self.url))

		# Setup the default configuration
		createFile(os.path.join(
			self.path, "conf", "%s.ini") % self.name)
		if default_config is not None:
			default_config.createConfig(os.path.join(
				self.path, "conf", "%s.ini") % self.name)
		self.loadConfig()

		# Create the database
		try:
			import default_db
			default_db.createDB(
					self.config.get(
						self.name, "database") % self.path)
		except ImportError:
			pass

	def verify(self):
		fd = open(os.path.join(self.path, "VERSION"), "r")
		try:
			version = fd.readlines()[0]
		except:
			version = ""
		fd.close()
		assert version.startswith("%s Environment" % self.name)
		self.version = int(
				version.split(
					"%s Environment Version" % self.name)[1].strip())

	def needsUpgrade(self):
		return VERSION > self.version

	def loadConfig(self):
		from config import Configuration
		self.config = Configuration(
				os.path.join(
					self.path, "conf", "%s.ini" % self.name))
		if default_config is not None:
			for section, name, value in default_config.CONFIG:
				self.config.setdefault(section, name, value)
	
	def setupLog(self):
		from log import newLogger

		logType = self.config.get("logging", "type")
		logLevel = self.config.get("logging", "level")
		logFile = self.config.get("logging", "file")
		if not os.path.isabs(logFile):
			logFile = os.path.join(self.path, "log", logFile)
		logID = self.path

		self.log = newLogger(logType, logFile, logLevel, logID)
	
	def loadDB(self):
		from pymills.db import Connection

		self.db = Connection(
				self.config.get(self.name, "database") % self.path)
