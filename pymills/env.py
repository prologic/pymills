# Filename: env.py
# Module:	env
# Date:		10th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Environment Container

This is a module to allow you to easily store config files,
templates, databases, log files and other things related
to your application easily. It also serves as a general
container for your application's running data. Instead
of passing heaps of instances around for various things,
just pass a single instance of Environment.
"""

import os

from config import Configuration

VERSION = 1

class BaseEnvironment:
	"""BaseEnvironment(path, name="PyMills",
	      version=VERSION, defaultConfig=[],
	      url="http://trac.shortcircuit.net.au/projects/pymills/",
	      create=False) -> new environment object
	
	Creates a new environment object that by default only
	holds a config file, log file and database.

	This should be sub-classes to provide an application
	specific environment.
	"""

	def __init__(self, path, name="PyMills",
			version=VERSION, defaultConfig=[],
			url="http://trac.shortcircuit.net.au/projects/pymills/",
			create=False):
		"initializes x; see x.__class__.__doc__ for signature"

		self.path = os.path.abspath(os.path.expanduser(path))
		self.name = name
		self.version = version
		self.defaultConfig = defaultConfig
		self.url = url

		if create:
			self.create()
		else:
			self.verify()

		self.loadConfig()
		self.setupLog()
		self.loadDB()

	def create(self):
		"""E.create() -> None

		Creates the environment. The environment given
		by self.path must not already exist.

		Sub-classes may override this to create their own
		custom environment and may also call this to
		create the default structure.
		"""

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

		# Create a few files
		createFile(os.path.join(self.path, "VERSION"),
				"%s Environment Version %d\n" % (
					self.name, VERSION))
		createFile(os.path.join(self.path, "README"),
				"This directory contains a %s environment.\n"
				"Visit %s for more information.\n" % (
					self.name, self.url))

		# Setup the default configuration
		configfile = os.path.join(
				self.path, "conf", "%s.ini") % self.name
		createFile(configfile)
		config = Configuration(configfile)
		for section, name, value in self.defaultConfig:
			config.set(section, name, value)
		config.save()
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
		"""E.verify() -> None

		Verify that the environment is valid.
		Sub-classes should not override this.
		"""

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
		"""E.needsUpgrade() -> bool

		Return True if the environment needs upgrading,
		otherwise return False.
		Sub-classes should not override this.
		"""

		return VERSION > self.version

	def loadConfig(self):
		"""E.loadConfig() -> None

		Load the configuration file from the environment.
		Sub-classes should not override this unless they
		want to load a different type of config file.
		By default INI-style config files are loaded
		using Python's Standard ConfigParser Library
		"""

		configfile = os.path.join(
				self.path, "conf", "%s.ini") % self.name
		self.config = Configuration(configfile)
		for section, name, value in self.defaultConfig:
			self.config.setdefault(section, name, value)
	
	def setupLog(self):
		"""E.setupLog() -> None

		Setup the log file, logging to the environment.
		Sub-classes should not override this unless they
		want to use their own logging mechanism.
		By default the Python's Standard log module
		is used.
		"""

		from log import newLogger

		name = self.name
		logType = self.config.get("logging", "type")
		logLevel = self.config.get("logging", "level")
		logFile = self.config.get("logging", "file")
		if not os.path.isabs(logFile):
			logFile = os.path.join(self.path, "log", logFile)
		logID = self.path

		self.log = newLogger(name, logType,
				logFile, logLevel, logID)
	
	def loadDB(self):
		"""E.loadDB() -> None

		Load the database from the environment.
		Sub-classes should not override this unless they
		want to use their own database library.
		By default the pymills.db library is used.
		"""

		from pymills.db import Connection

		self.db = Connection(
				self.config.get(self.name, "database") % self.path)
