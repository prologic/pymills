# Filename: web.py
# Module:	web
# Date:		27th September 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Web Library

This module contains classes to assist in building web-based
applications in python wether you're using plain CGI or
mod_python
"""

import re

def setupPaths(req, PYTHONPATH=None):

	import os
	import sys

	if PYTHONPATH is None:
		PYTHONPATH = os.getenv("PYTHONPATH", os.getcwd())

	if not PYTHONPATH in sys.path:
		sys.path.append(PYTHONPATH)

	docpath = os.path.dirname(req.filename)
	if not docpath in sys.path:
		sys.path.append(docpath)
	docroot = "http://%s%s" % (
			req.hostname, os.path.dirname(req.uri))
	return (docroot, docpath)

class Template:

	def __init__(self, docpath="."):
		self._docpath = docpath
		self._content = ""
		self._vars = {}
	
	def __str__(self):
		return self._content % self._vars

	def __setitem__(self, key, value):
		self._vars[key] = value
	
	def load(self, filename):
		path = self._docpath
		self._content = open("%s/%s" % (path, filename), 'r').read()
		# %\((.*?)\)s
		vars = re.findall("%\((.*?)\)", self._content,
				re.MULTILINE + 
				re.DOTALL)
		for key in vars:
			self._vars[key] = ""
	
class Theme:

	def __init__(self, themepath="."):
		self._themepath = themepath
		self._templates = []
		self._content = ""
	
	def load(self, theme):
		file = "%s/%s/theme.def" % (self._themepath, theme)
		for i, line in enumerate(open(file, 'r').readlines()):
			pass
