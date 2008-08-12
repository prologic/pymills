# Filename: log.py
# Module:	log
# Date:		11th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Log

...
"""

import sys
import logging

from event import *

###
### Events
###

class Log(Event):
	"""Log(Event) -> Log Event

	args: level, msg
	"""

class Debug(Log):
	"""Debug(Log) -> Debug Log Event

	args: msg
	"""

class Info(Log):
	"""Info(Log) -> Info Log Event

	args: msg
	"""

class Warning(Log):
	"""Warning(Log) -> Warning Log Event

	args: msg
	"""

class Error(Log):
	"""Error(Log) -> Error Log Event

	args: msg
	"""

class Exception(Log):
	"""Exception(Log) -> Exception Log Event

	args: msg
	"""

class Critical(Log):
	"""Critical(Log) -> Critical Log Event

	args: msg
	"""

###
### Components
###

class Logger(Component):

	channel = "log"

	def __init__(self, name, type, filename, level):
		super(Logger, self).__init__()

		self.logger = logging.getLogger(name)

		type = type.lower()
		if type == "file":
			hdlr = logging.FileHandler(filename)
		elif type in ["winlog", "eventlog", "nteventlog"]:
			# Requires win32 extensions
			hdlr = logging.handlers.NTEventLogHandler(name, type="Application")
		elif type in ["syslog", "unix"]:
			hdlr = logging.handlers.SysLogHandler("/dev/log")
		elif type in ["stderr"]:
			hdlr = logging.StreamHandler(sys.stderr)
		else:
			raise ValueError

		format = name + "[%(module)s] %(levelname)s: %(message)s"
		if type == "file":
			format = "%(asctime)s " + format
		dateFormat = ""
		level = level.upper()
		if level in ["DEBUG", "ALL"]:
			self.logger.setLevel(logging.DEBUG)
			dateFormat = "%X"
		elif level == "INFO":
			self.logger.setLevel(logging.INFO)
		elif level == "ERROR":
			self.logger.setLevel(logging.ERROR)
		elif level == "CRITICAL":
			self.logger.setLevel(logging.CRITICAL)
		else:
			self.logger.setLevel(logging.WARNING)

		formatter = logging.Formatter(format,dateFormat)
		hdlr.setFormatter(formatter)
		self.logger.addHandler(hdlr)

	@listener("debug")
	def onDEBUG(self, msg, *args, **kwargs):
		self.logger.debug(msg, *args, **kwargs)

	@listener("info")
	def onINFO(self, msg, *args, **kwargs):
		self.logger.info(msg, *args, **kwargs)

	@listener("warn")
	def onWARNING(self, msg, *args, **kwargs):
		self.logger.warning(msg, *args, **kwargs)

	onWARN = onWARNING
	onWARN.channel = "warn"

	@listener("error")
	def onERROR(self, msg, *args, **kwargs):
		self.logger.error(msg, *args, **kwargs)

	@listener("exception")
	def onEXCEPTION(self, msg, *args):
		self.logger.exception(msg, *args)

	@listener("critical")
	def onCRITICAL(self, msg, *args, **kwargs):
		self.logger.critical(msg, *args, **kwargs)

	onFATAL = onCRITICAL
	onFATAL.channel = "fatal"

	@listener("log")
	def onLOG(self, level, msg, *args, **kwargs):
		self.logger.log(level, msg, *args, **kwargs)
