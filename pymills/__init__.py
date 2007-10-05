# Filename: __init__.py
# Module:	__init__
# Date:		04th August 2004
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""James Mills Python Library

pymills is a collection of works by James Mills containing
general purpose and special purpose libraries and modules
for the Python programming language. Most libraries and
modules are based around a core component of pymills, the
"event" library.

pymills provides a very easy to use and powerful event
library enabling asyncronous and event-driven applications
and system to be developed. Software systems and applications
written with pymills.event are broken up into components
and can be distributed across different nodes.

pymills also contains an ann library which provides the
building blocks to build artificial neural networks in
an asyncronous/event-driven manner closely modelling
biological neural networks.
"""

__name__ = "pymills"
__description__ = "James Mills Python Library"
__version__ = "3.3.1"
__author__ = "James Mills"
__author_email__ = "%s, prologic at shortcircuit dot net dot au" % __author__
__maintainer__ = __author__
__maintainer_email__ = __author_email__
__url__ = "http://trac.shortcircuit.net.au/pymills/"
__download_url__ = "http://shortcircuit.net.au/~prologic/downloads/software/%s-%s.tar.gz" % (__name__, __version__)
__copyright__ = "CopyRight (C) 2005-2007 by %s" % __author__
__license__ = "GPL"
__platforms__ = "POSIX"
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

__package_data__ = {
		}

__install_requires__ = [
		]

__setup_requires__ = [
		]

__extras_require__ = {
		}

__entry_points__ = """
"""

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
