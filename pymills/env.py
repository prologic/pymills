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

from event import *
from log import Logger
from config import Config, LoadConfig, SaveConfig

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

class CreateEnv(Event):
	"""CreateEnv(Event) -> CreateEnv Event"""

class LoadEnv(Event):
	"""LoadEnv(Event) -> LoadEnv Event"""

class EnvCreated(Event):
	"""EnvCreated(Event) -> EnvCreated Event"""

class EnvLoaded(Event):
	"""EnvLoaded(Event) -> Loaded Event"""

class EnvInvalid(Event):
	"""EnvInvalid(Event) -> EnvInvalid Event

	args: path, msg
	"""

class EnvNeedsUpgrade(Event):
	"""EnvNeedsUpgrade(Event) -> EnvNeedsUpgrade Event

	args: path, msg
	"""

class EnvUpgraded(Event):
	"""EnvUpgraded(Event) -> Upgraded Event"""

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
	 * EnvCreated
	 * EnvLoaded
	 * EnvInvalid
	 * EnvNeedsUpgrade
	 * EnvUpgraded
	"""

	channel = "env"

	version = VERSION
	config = CONFIG

	def __init__(self, path, name, config=None):
		super(Environment, self).__init__()

		self.path = os.path.abspath(os.path.expanduser(path))
		self.name = name

		if config:
			self.config.update(config)

	@listener("create")
	def onCREATE(self):
		"""E.onCREATE()

		Create a new Environment. The Environment path given
		by self.path must not already exist.
		"""

		# Create the directory structure
		os.mkdir(self.path)
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
		config = Config(configfile)
		config.read(configfile)
		for section in self.config:
			if not config.has_section(section):
				config.add_section(section)
			for option, value in self.config[section].iteritems():
				config.set(section, option, value)
		config.write(open(configfile, "w"))

		self.push(EnvCreated(), "created", self.channel)

	@listener("verify")
	def onVERIFY(self, load=False):
		"""E.onVERIFY(load=False) -> None

		Verify the Environment by checking it's version against
		the expected version.

		If the Environment's version does not match, send
		an EnvNeedsUpgrade event. If the Environment is
		invalid and cannot be read, send an EnvInvalid
		event. If load=True, send a LoadEnv event.
		"""

		with open(os.path.join(self.path, "VERSION"), "r") as f:
			version = f.read().strip()
			if not version:
				msg = "No Environment version information"
				self.push(EnvInvalid(self.env.path, msg), "invalid", self.channel)
			else:
				try:
					verion = int(version)
					if self.version > version:
						self.push(
								EnvNeedsUpgrade(self.env.path),
								"needsupgrade",
								self.channel)
				except ValueError:
					msg = "Environment version information invalid"
					self.push(
							EnvInvalid(self.env.path, msg),
							"invalid",
							self.channel)

		if load:
			self.push(LoadEnv90, "load", self.channel)

	@listener("load")
	def onLOAD(self, verify=False):
		"""E.onLOAD(verify=False) -> None

		Load the Environment. Load the configuration and logging
		components. If verify=True, verify the Environment first.
		"""

		if verify:
			self.push(VerifyEnv(load=True), "verify", self.channel)
		else:

			# Create Config Component
			configfile = os.path.join(self.path, "conf", "%s.ini" % self.name)
			self.config = Config(configfile)
			self.manager += self.config
			self.push(LoadConfig(), "load", "config")

			# Create Logger Component
			logname = self.name
			logtype = self.config.get("logging", "type")
			loglevel = self.config.get("logging", "level")
			logfile = config.get("logging", "file") % {"name": self.name}
			if not os.path.isabs(logfile):
				logfile = os.path.join(self.path, logfile)
			self.log = Logger(logname, logtype, loglevel, logfile)
			self.manager += self.log

			self.push(EnvLoaded(), "loaded", self.channel)
