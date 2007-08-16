# Filename: __init__.py
# Module:	__init__
# Date:		04th August 2004
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""James Mills Python Library

This is my library of packages and modules that I have
devloped for various purposes.

All modules and packages are written by me, James Mills and are
therefore CopyRight (C) 2003-2005 by James Mills.
This library is released under the GPL license which is
included with this distribution. Please read it.

I hope you will find this libary usefull in some way, I use it
in all my Python Software Projects. Currently:
	* PircSrv -> http://trac.shortcircuit.net.au/pircsrv/
	* PIRCD   -> No HomePage.
	* KDB     -> No HomePage.
See the ShortCircuit GitWeb: http://git.shortcircuit.net.au/

Please report any defects you find with this library or any of
the parts therein. There is a defect tracking tool on the url
shown above. Please follow the links to the pymills project
page.

cheers
JamesMills
"""

__name__ = "pymills"
__description__ = "James Mills Python Library"
__version__ = "3.2.12-git3"
__author__ = "James Mills"
__author_email__ = "%s, prologic at shortcircuit dot net dot au" % __author__
__maintainer__ = __author__
__maintainer_email__ = __author_email__
__url__ = "http://trac.shortcircuit.net.au/pymills/"
__download_url__ = "http://shortcircuit.net.au/~prologic/downloads/software/%s-%s.tar.gz" % (__name__, __version__)
__copyright__ = "CopyRight (C) 2005-2007 by %s" % __author__
__license__ = "GPL"
__platform__ = ""
__keywords__ = "James Mills Python Library General Purpose"
__classifiers__ = [
		"Development Status :: 3 - Alpha",
		"Development Status :: 4 - Beta",
		"Development Status :: 5 - Production/Stable",
		"Environment :: Other Environment",
		"Intended Audience :: Developers",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Adaptive Technologies",
		"Topic :: Communications :: Chat :: Internet Relay Chat",
		"Topic :: Database :: Front-Ends",
		"Topic :: Scientific/Engineering :: Artificial Intelligence",
		"Topic :: Software Development :: Libraries",
		"Topic :: Software Development :: Libraries :: Application Frameworks",
		"Topic :: Software Development :: Libraries :: Python Modules",
		]
__str__ = "%s-%s" % (__name__, __version__)

__all__ = (
		"ann",
		"datatypes",
		"db",
		"env",
		"event",
		"io",
		"irc",
		"log",
		"mem",
		"misc",
		"semnet",
		"sockets",
		"spider",
		"test",
		"timers",
		"utils",
		"ver",
		"web",
		)
