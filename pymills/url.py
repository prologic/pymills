# Filename: url.py
# Module:	url
# Date:		28 September 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""URL Library

Various functions for URL manipulation
"""

def unescape(url):
	return url.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
