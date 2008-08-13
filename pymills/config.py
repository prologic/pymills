# Module:	config
# Date:		13th August 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Config

Configuration Component. This component uses the  standard
ConfigParser.ConfigParser class and adds support for saving
the configuration to a file.
"""

from __future__ import with_statement

from ConfigParser import ConfigParser

from event import *


###
### Events
###

class LoadConfig(Event):
	"""LoadConfig(Event) -> LoadConfig Event"""

class SaveConfig(Event):
	"""SaveConfig(Event) -> SaveConfig Event"""

###
### Components
###

class Config(Component, ConfigParser):

	channel = "config"

	def __init__(self, filename, defaults=None):
		Component.__init__(self)
		ConfigParser.__init__(self, defaults=defaults)

		self.filename = filename

	def get(self, section, option, default=None, raw=False, vars=None):
		if self.has_option(section, option):
			return super(Config, self).get(section, option, raw, vars)
		else:
			return default

	def getint(self, section, option, default=0):
		return int(self.get(section, option, default))

	def getfloat(self, section, option, default=0.0):
		return float(self.get(section, option, default))

	def getboolean(self, section, option, default=False):
		return bool(self.get(section, option, default))

	@listener("load")
	def onLOAD(self):
		"""C.onLOAD()

		Load the configuration file.
		"""

		self.read(self.filename)

	@listener("save")
	def onSAVE(self):
		"""C.onSAVE()

		Save the configuration file.
		"""

		with open(self.configfile, "w") as f:
			self.write(f)
