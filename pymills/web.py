# Filename: web.py
# Module:	web
# Date:		27th September 2005
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Web Library

This module contains classes to assist in building web-based
applications in python wether you're using plain CGI or
mod_python
"""

def setupPaths(req, PYTHONPATH=None):
	"""Return the root paths of the current url given
	in req. That is: docroot and docpath.

	NOTE: This function only works with mod_python

	
	req        - mod_python Request object
	PYTHONPATH - custom path to append to python's searchable
	             path.
	
	Usage:
	docroot, docpath = setupPaths(req)
	"""

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

def decodeHTMLEntities(text):
	"""Decode HTML entitiesC &amp; &lt; &gt; and &#34;"""

	if not text:
		return ""
	return str(text).replace("&amp;", "&") \
			.replace("&lt;", "<") \
			.replace("&gt;", ">") \
			.replace("&quot;", "\"") \
			.replace("&#039;", "'")

def encodeHTMLEntities(text):
	"""Convert & < > and \" to their relevant HTML entities."""

	if not text:
		return ""
	return str(text).replace("&", "&amp;") \
			.replace("<", "&lt;") \
			.replace(">", "&gt;") \
			.replace("\"", "&quot;") \
			.replace("'", "&#039;")

