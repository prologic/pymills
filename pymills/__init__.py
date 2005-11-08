# Filename: __init__.py
# Module:	__init__
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""James Mills Python Library

This is my library of packages and modules that I have
devloped for various purposes.

All modules and packages are written by me, James Mills and are
therefore CopyRight (C) 2003-2005 by James Mills.
This library is released under the GPL license which is
included with this distribution. Please read it.

I hope you will find this libary usefull in some way, I use it
in all my Python Software Projects. For a list of projects
implemented using this library and Python please see:
	http://shortcircuit.net.au/~prologic/ and follow the links.

Please report any defects you find with this library or any of
the parts therein. There is a defect tracking tool on the url
shown above. Please follow the links to the pymills project
page.

cheers
JamesMills
"""

__name__ = "pymills"
__desc__ = "James Mills Python Library"
__version__ = "0.8.0"
__author__ = "James Mills"
__email__ = "%s <prologic@shortcircuit.net.au>" % __author__
__url__ = "http://shortcircuit.net.au/~prologic/"
__copyright__ = "CopyRight (C) 2005 by %s" % __author__
__license__ = "GPL"
__str__ = "%s-%s" % (__name__, __version__)

__all__ = [
		"utils",
		"cmdopt",
		"io",
		"ircbot",
		"sockets",
		"utils",
		"adt",
		"db",
		"irc",
		"misc",
		"timers",
		"ver",
		"spider",
		"web",
		"url"
	]
