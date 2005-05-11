#!/usr/bin/env python

# Filename: misc.py
# Module:   misc
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-08 21:16:31 +1000 (Fri, 08 Apr 2005) $
# $Author: prologic $
# $Id: Math.py 1572 2005-04-08 11:16:31Z prologic $

"""Math

Math module containg various math routines.
"""

__version__ = "0.1"
__copyright__ = "CopyRight (C) 2005 by James Mills"
__author__ = "James Mills <prologic@shortcircuit.net.au>"
__url__ = "http://shortcircuit.net.au/~prologic/"

def addPercent(value, percentage):
	"Add percentage to value returning new value"

	return float(value) * ((float(percentage) / 100.0) + 1.0)

def subPercent(value, percentage):
	"Subtract percentage to value returning new value"

	return float(value) / ((float(percentage) / 100.0) + 1.0)

def bytes(bytes):
	"""Return a human-readable form of bytes

	bytes - number of bytes

	Returns:
	(float, str)

	Where:
	float - is either a B, KB, MB, GB, TG representation of bytes
	str   - is the postfix, either one of: B, KB, MB, GB, TG
	"""

	if bytes >= 1024**4:
		return (round(bytes / float(1024**4), 2), "TB")
	elif bytes >= 1024**3:
		return (round(bytes / float(1024**3), 2), "GB")
	elif bytes >= 1024**2:
		return (round(bytes / float(1024**2), 2), "MB")
	elif bytes >= 1024**1:
		return (round(bytes / float(1024**1), 2), "KB")
	else:
		return (bytes, "B")

def duration(seconds):
	"Returns the human-radable duration of seconds"

	days = int(seconds / 60 / 60 / 24)
	seconds = (seconds) % (60 * 60 * 24)
	hours = int((seconds / 60 / 60))
	seconds = (seconds) % (60 * 60)
	mins = int((seconds / 60))
	seconds = int((seconds) % (60))

	return str(days) + 'd ' + str(hours) + 'h ' + str(mins) + 'm ' + str(seconds) + 's'

#" vim: tabstop=3 nocindent autoindent
