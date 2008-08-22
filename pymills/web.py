# Filename: web.py
# Module:	web
# Date:		27th September 2005
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Web Server Library

This module wraps up various components into a compact
Web Server Framework. The framework is compatible with
CherryPy's request object and thus compatible with most
of CherryPy's tools/filters.
"""

from pymills.net.http import HTTP
from pymills.net.sockets import TCPServer

class Server(TCPServer, HTTP): pass
