# Filename: misc.py
# Module:   misc
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-08 21:16:31 +1000 (Fri, 08 Apr 2005) $
# $Author: prologic $
# $Id: Math.py 1572 2005-04-08 11:16:31Z prologic $

"""Miscellaneous Module"""

def addPercent(value, percentage):
	return float(value) * ((float(percentage) / 100.0) + 1.0)

def subPercent(value, percentage):
	return float(value) / ((float(percentage) / 100.0) + 1.0)

def bytes(bytes):
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
	days = int(seconds / 60 / 60 / 24)
	seconds = (seconds) % (60 * 60 * 24)
	hours = int((seconds / 60 / 60))
	seconds = (seconds) % (60 * 60)
	mins = int((seconds / 60))
	seconds = int((seconds) % (60))

	return "%dd %dh %dm %ds" % (days, hours, mins, secs)
