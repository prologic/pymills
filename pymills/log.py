# Filename: log.py
# Module:	log
# Date:		11th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: cli.py 170 2006-02-23 06:24:58Z prologic $

"""Log

...
"""

import sys

def newLogger(logType="syslog", logFile=None, level="WARNING",
		logID="PIRCSrv"):

	import logging
	import logging.handlers

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

	format = "PIRCSrv[%(module)s] %(levelname)s: %(message)s"
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
