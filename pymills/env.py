# Module:	env
# Date:		10th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Environment Component

An Environment Component that by default sets up a COnfig and Logger
component and is used to create, load and manage system/application
environments.
"""

from __future__ import with_statement

import os

import config
from event import *
from log import Logger
from config import Config

###
### Constants
###

VERSION = 1

CONFIG = {
		"general": {
			"pidfile": os.path.join("log", "%(name)s.pid"),
			"debug": False
			},
		"logging": {
			"type": "file",
			"file": os.path.join("log", "%(name)s.log"),
			"level": "INFO"
			}
		}

###
### Functions
###

def createFile(filename, data=None):
	fd = open(filename, "w")
	if data:
		fd.write(data)
	fd.close()

###
### Events
###

class Create(Event):
	"""Create(Event) -> Create Event"""

class Load(Event):
	"""Load(Event) -> Load Event"""

class Upgrade(Event):
	"""Upgrade(Event) -> Upgrade Event"""

class Created(Event):
	"""Created(Event) -> Created Event"""

class Loaded(Event):
	"""Loaded(Event) -> Loaded Event"""

class Invalid(Event):
	"""Invalid(Event) -> Invalid Event

	args: path, msg
	"""

class NeedsUpgrade(Event):
	"""NeedsUpgrade(Event) -> NeedsUpgrade Event

	args: path, msg
	"""

class Upgraded(Event):
	"""Upgraded(Event) -> Upgraded Event"""

###
### Components
###

class Environment(Component):
	"""Environment(path, name, version=VERSION, config=CONFIG) -> Environment

	Creates a new environment component that by default only
	holds configuration and logger components.

	This component can be extended to provide more complex
	system and application environments. This component will
	expose the following events:
	 * Created
	 * Loaded
	 * Invalid
	 * NeedsUpgrade
	 * Upgraded
	"""

	channel = "env"

	version = VERSION

	def __init__(self, path, name):
		super(Environment, self).__init__()

		self.path = os.path.abspath(os.path.expanduser(path))
		self.name = name

	@listener("create")
	def onCREATE(self):
		"""E.onCREATE()

		Create a new Environment. The Environment path given
		by self.path must not already exist.
		"""

		# Create the directory structure
		os.makedirs(self.path)
		os.mkdir(os.path.join(self.path, "log"))
		os.mkdir(os.path.join(self.path, "conf"))

		# Create a few files
		createFile(os.path.join(self.path, "VERSION"), "%d" % self.version)
		createFile(
				os.path.join(self.path, "README"),
				"This directory contains a %s Environment." % self.name)

		# Setup the default configuration
		configfile = os.path.join(self.path, "conf", "%s.ini" % self.name)
		createFile(configfile)
		self.config = Config(configfile)
		self.manager += self.config
		self.send(config.Load(), "load", "config")
		for section in CONFIG:
			if not self.config.has_section(section):
				self.config.add_section(section)
			for option, value in CONFIG[section].iteritems():
				if type(value) == str:
					value = value % {"name": self.name}
				self.config.set(section, option, value)
		self.send(config.Save(), "save", "config")

		self.send(Created(), "created", self.channel)

	@listener("verify")
	def onVERIFY(self, load=False):
		"""E.onVERIFY(load=False)

		Verify the Environment by checking it's version against
		the expected version.

		If the Environment's version does not match, send
		an EnvNeedsUpgrade event. If the Environment is
		invalid and cannot be read, send an Invalid
		event. If load=True, send a Load event.
		"""

		with open(os.path.join(self.path, "VERSION"), "r") as f:
			version = f.read().strip()
			if not version:
				msg = "No Environment version information"
				self.push(Invalid(self.env.path, msg), "invalid", self.channel)
			else:
				try:
					verion = int(version)
					if self.version > version:
						self.push(
								NeedsUpgrade(self.env.path),
								"needsupgrade",
								self.channel)
				except ValueError:
					msg = "Environment version information invalid"
					self.push(
							Invalid(self.env.path, msg),
							"invalid",
							self.channel)

		if load:
			self.push(Load(), "load", self.channel)

	@listener("load")
	def onLOAD(self, verify=False):
		"""E.onLOAD(verify=False)

		Load the Environment. Load the configuration and logging
		components. If verify=True, verify the Environment first.
		"""

		if verify:
			self.push(Verify(load=True), "verify", self.channel)
		else:

			# Create Config Component
			configfile = os.path.join(self.path, "conf", "%s.ini" % self.name)
			self.config = Config(configfile)
			self.manager += self.config
			self.send(config.Load(), "load", "config")

			# Create Logger Component
			logname = self.name
			logtype = self.config.get("logging", "type", "file")
			loglevel = self.config.get("logging", "level", "INFO")
			logfile = self.config.get("logging", "file", "/dev/null")
			logfile = logfile % {"name": self.name}
			if not os.path.isabs(logfile):
				logfile = os.path.join(self.path, logfile)
			self.log = Logger(logfile, logname, logtype, loglevel)
			self.manager += self.log

			self.push(Loaded(), "loaded", self.channel)
