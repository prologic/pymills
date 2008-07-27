#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import optparse
from time import sleep
from socket import gethostname

from pymills.event import *
from pymills.net.irc import IRC
from pymills.net.sockets import TCPClient
from pymills import __version__ as systemVersion

USAGE = "%prog [options] <host> [<port>]>"
VERSION = "%prog v" + systemVersion

###
### Functions
###

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-s", "--ssl",
			action="store_true", default=False, dest="ssl",
			help="Enable Secure Socket Layer (SSL)")
	parser.add_option("-d", "--debug",
			action="store_true", default=False, dest="debug",
			help="Enable debug mode. (Default: False)")

	opts, args = parser.parse_args()

	if len(args) < 1:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

###
### Components
###

class Bot(TCPClient, IRC): pass

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in args[0]:
		host, port = args[0].split(":")
		port = int(port)
	else:
		host = args[0]
		port = 6667

	debugger.set(opts.debug)
	debugger.IgnoreEvents = ["Read", "Write", "Raw"]

	bot = Bot(e)

	bot.open(host, port, opts.ssl)

	bot.ircUSER("test", gethostname(), host, "Test Bot")
	bot.ircNICK("test")

	while bot.connected:
		try:
			e.flush()
			bot.poll()
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			bot.ircQUIT()

###
### Entry Point
###

if __name__ == "__main__":
	main()
