# Filename: misc.py
# Module:	misc
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Miscellaneous

Various miscellaneous functions that don't fit
Use as documented.
"""

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
	return (days, hours, mins, seconds)

def backMerge(l, n, t=" "):
	"""Merge the last n items in list l joining with tokens t

	l - list
	n - merge last n items from l
	t - token (default: " ")
	"""
	return l[:-n] + [t.join(l[-n:])]
