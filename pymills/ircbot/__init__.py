# Filename: __init__.py
# Module:   __init__
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""IRCBot Module

IRCBot Module which makes creating IRC Bots really easy!
See: test.py for an example.
"""

__name__ = "ircbot"
__desc__ = "IRC Bot Module"
__version__ = "0.1.1"
__author__ = "James Mills"
__email__ = "James Mills <prologic@shortcircuit.net.au>"
__url__ = "http://shortcircuit.net.au/~prologic/"
__copyright__ = "CopyRight (C) 2005 by James Mills"
__str__ = "%s-%s" % (__name__, __version__)

from ircbot import core
from ircbot import timers
