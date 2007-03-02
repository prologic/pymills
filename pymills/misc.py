# Filename: misc.py
# Module:	misc
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Miscellaneous

Various miscellaneous functions that don't fit
Use as documented.
"""

def hmsToSeconds(h, m, s=0):
	return h*3600 + m*60 + s

def getTotalTime(s, e):
	if e < s:
		return ((60*60*24) + e) - s
	else:
		return e - s

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
		return bytes, "B"

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

def strToBool(s):
	return s.lower() in [
			"yes",
			"yeah",
			"1",
			"true",
			"ok",
			"okay",
			"k"]

def beat():
	from time import localtime, timezone
	x = localtime()

	y = (x[3] * 3600) + (x[4] * 60) + x[5]
	y += timezone + 3600

	if x[8] == 1:
		y -= 3600

	y = (y * 1000) / 86400.0

	if y > 1000:
		y -= 1000
	elif y < 0:
		y += 1000

	return y
