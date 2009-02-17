# Filename: log.py
# Module:	log
# Date:		11th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Log

...
"""

def newLogger(name="PyMills", logType="syslog",
		logFile=None, level="WARNING", logID="PyMills"):

	import sys
	import logging

	logger = logging.getLogger(logID)

	logType = logType.lower()
	if logType == "file":
		hdlr = logging.FileHandler(logFile)
	elif logType in ["winlog", "eventlog", "nteventlog"]:
		# Requires win32 extensions
		hdlr = logging.handlers.NTEventLogHandler(logID,
				logType="Application")
	elif logType in ["syslog", "unix"]:
		hdlr = logging.handlers.SysLogHandler("/dev/log")
	elif logType in ["stderr"]:
		hdlr = logging.StreamHandler(sys.stderr)
	else:
		raise ValueError

	format = name + "[%(module)s] %(levelname)s: %(message)s"
	if logType == "file":
		format = "%(asctime)s " + format
	dateFormat = ""
	level = level.upper()
	if level in ["DEBUG", "ALL"]:
		logger.setLevel(logging.DEBUG)
		dateFormat = "%X"
	elif level == "INFO":
		logger.setLevel(logging.INFO)
	elif level == "ERROR":
		logger.setLevel(logging.ERROR)
	elif level == "CRITICAL":
		logger.setLevel(logging.CRITICAL)
	else:
		logger.setLevel(logging.WARNING)

	formatter = logging.Formatter(format,dateFormat)
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)

	return logger
