#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import optparse
from time import sleep

from pymills.net.irc import IRC
from pymills.net.sockets import TCPClient
from pymills import __version__ as systemVersion
from pymills.event import Manager, filter, listener

USAGE = "%prog [options] <host> [<port>]>"
VERSION = "%prog v" + systemVersion

class Bot(TCPClient, IRC):

	def __init__(self, event):
		super(Bot, self).__init__(event)

	@filter()
	def onDEBUG(self, event):
		print event
		return False, event

	@listener("raw")
	def onRAW(self, data):
		self.write(data + "\r\n")

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-s", "--ssl",
			action="store_true", default=False, dest="ssl",
			help="Enable Secure Socket Layer (SSL)")

	opts, args = parser.parse_args()

	if len(args) < 1:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

def main():
	opts, args = parse_options()

	host = args[0]
	if len(args) > 1:
		try:
			port = int(args[1])
		except:
			port = 6667
	else:
		port = 6667

	event = Manager()
	bot = Bot(event)

	bot.open(host, port, opts.ssl)

	bot.ircUSER("test", "localhost", "localhost", "Test Bot")
	bot.ircNICK("test")

	while True:
		if bot.connected:
			bot.process()
		event.flush()
		sleep(0.5)

if __name__ == "__main__":
	main()
