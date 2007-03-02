# Filename: mem.py
# Module:	mem
# Date:		2nd March 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Memory

This module contains functions to return the memory
usage of an application.
"""
import os

_proc_status = "/proc/%d/status" % os.getpid()

_scale = {"KB": 1024.0, "MB": 1024.0 * 1024.0}

def _VmB(VmKey):
	try:
		t = open(_proc_status)
		v = t.read()
		t.close()
	except:
		return 0.0
	i = v.index(VmKey)
	v = v[i:].split(None, 3)
	if len(v) < 3:
		return 0.0
	return float(v[1]) * _scale[v[2].upper()]

def memory(since=0.0):
	"Return memory usage in bytes."

	return _VmB("VmSize:") - since

def resident(since=0.0):
	"Return resident memory usage in bytes."

	return _VmB("VmRSS:") - since

def stacksize(since=0.0):
	"Return stack size in bytes."

	return _VmB("VmStk:") - since
