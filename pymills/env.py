# Module:	env
# Date:		10th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Environment Container

This module contains a base environment that normally should be sub-classed to
implement an application/system specific environment. An environment is
designed to act as a container for things like:
 * config file
 * logging
 * database connections
 * event managers
 * etc...

Instead of passing multiple objects around a system, you can pass a single
instance of an environment which holds all the objects needed by a system.
"""

import os

from log import newLogger
from utils import ConfigParser

VERSION = 1

CONFIG = []

class BaseEnvironment(object):
	"""BaseEnvironment(path, name="pymills", version=VERSION, config=CONFIG,
			create=False) -> new environment object

	Creates a new environment object that by default only
	holds configfile and log instances.

	This should be sub-classed to provide an application
	specific environment.
	"""

	def __init__(self, path, name="pymills", version=VERSION, config=CONFIG,
		create=False):
		"initializes x; see x.__class__.__doc__ for signature"

		self.path = os.path.abspath(os.path.expanduser(path))
		self.name = name
		self.version = version
		self.config = config

		if create:
			self.create()
		else:
			self.verify()

		self.loadConfig()
		self.setupLog()

	def reload(self):
		"""E.reload() -> None

		Reloads the environment.
		By default this only reloads the config file.

		Sub-classes may override this to create their
		own custom reload method and may also call this to
		reload the default items.
		"""

		self.loadConfig()

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
		os.mkdir(os.path.join(self.path, "log"))
		os.mkdir(os.path.join(self.path, "conf"))

		# Create a few files
		createFile(os.path.join(self.path, "VERSION"),
				"%s Environment Version %d\n" % (
					self.name, self.version))
		createFile(os.path.join(self.path, "README"),
				"This directory contains a %s environment." % self.name)

		# Setup the default configuration
		configfile = os.path.join(
				self.path, "conf", "%s.ini") % self.name
		createFile(configfile)
		config = ConfigParser()
		config.read(configfile)
		for section, name, value in self.config:
			if not config.has_section(section):
				config.add_section(section)
			config.set(section, name, value)
		fp = open(configfile, "w")
		config.write(fp)
		fp.close()
		self.loadConfig()

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
		self.config = ConfigParser()
		self.config.read(configfile)
		self.config.path = configfile

	def setupLog(self):
		"""E.setupLog() -> None

		Setup the log file, logging to the environment.
		Sub-classes should not override this unless they
		want to use their own logging mechanism.
		By default the Python's Standard log module
		is used.
		"""

		name = self.name
		logType = self.config.get("logging", "type")
		logLevel = self.config.get("logging", "level")
		logFile = self.config.get("logging", "file")
		if not os.path.isabs(logFile):
			logFile = os.path.join(self.path, logFile)
		logID = self.path

		self.log = newLogger(name, logType,
				logFile, logLevel, logID)