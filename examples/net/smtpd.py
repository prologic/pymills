#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""MTA/MDA

Simple SMTP Server / Mail Transfer Agent (MTA) and Mail Delivery Agent (MDA).
Mail is delivered into Maildir mailboxes. No filterting or forwarding support
is available. The MTA only implements the minimum required set of SMTP
commands.
"""

import os
import sys
import optparse
from mailbox import Maildir
from traceback import format_exc

from pymills import event
from pymills.event import *
from pymills import __version__
from pymills.net.smtp import SMTP
from pymills.utils import daemonize
from pymills.net.sockets import TCPServer

USAGE = "%prog [options]"
VERSION = "%prog v" + __version__

###
### Functions
###

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-d", "--daemon",
			action="store_true", default=False, dest="daemon",
			help="Enable daemon mode (Default: False)")
	parser.add_option("-b", "--bind",
			action="store", type="str", default="0.0.0.0:25", dest="bind",
			help="Bind to address:[port]")
	parser.add_option("-p", "--path",
			action="store", default="/var/mail/", dest="path",
			help="Path to store mailI (Default: /var/mail/)")

	opts, args = parser.parse_args()

	return opts, args

###
### Components
###

class MDA(Component):

	def __init__(self, *args, **kwargs):
		super(MDA, self).__init__(*args, **kwargs)

		self.__path = kwargs.get("path", "/var/mail/")

	@listener("message")
	def onMESSAGE(self, sock, mailfrom, rcpttos, data):
		for recipient in rcpttos:
			self.deliver(data, recipient)
		data.close()

	def deliver(self, message, recipient):
		user, domains = recipient.split("@")
		mailbox = Maildir(os.path.join(self.__path, user), factory=None)
		mailbox.add(message)
		mailbox.flush()
		mailbox.close()

class MTA(TCPServer, SMTP):

	@listener("helo")
	def onHELO(self, sock, hostname):
		print >> sys.stderr, "%s Got HELO, hostname: %s" % (sock, hostname)

	@listener("mail")
	def onMAIL(self, sock, sender):
		print >> sys.stderr, "%s Got MAIL, sender: %s" % (sock, sender)

	@listener("rcpt")
	def onRCPT(self, sock, recipient):
		print >> sys.stderr, "%s Got RCPT, recipient: %s" % (sock, recipient)

	@listener("noop")
	def onNOOP(self, sock):
		print >> sys.stderr, "%s Got NOOP" % sock

	@listener("rset")
	def onRSET(self, sock):
		print >> sys.stderr, "%s Got RSET" % sock

	@listener("data")
	def onDATA(self, sock):
		print >> sys.stderr, "%s Got DATA" % sock

	@listener("quit")
	def onQUIT(self, sock):
		print >> sys.stderr, "%s Got QUIT" % sock

	@listener("disconnect")
	def onQUIT(self, sock):
		print >> sys.stderr, "%s Disconnected" % sock

	@listener("error")
	def onERROR(self, sock, error):
		print >> sys.stderr, "%s Error: %s" % (sock, error)

	@listener("message")
	def onMESSAGE(self, sock, mailfrom, rcpttos, data):
		print >> sys.stderr, "New Mail Message\n"
		print >> sys.stderr, "From: %s" % mailfrom
		print >> sys.stderr, "To: %s\n" % ",".join(rcpttos)

		for line in data:
			print >> sys.stderr, line

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 25

	path = opts.path
	daemon = opts.daemon

	if not os.path.exists(path):
		os.makedirs(path)

	mta = MTA(port, address)
	event.manager += mta
	event.manager += MDA(path=opts.path)

	while True:
		try:
			manager.flush()
			mta.poll()
		except UnhandledEvent:
			pass
		except Exception, error:
			print >> sys.stderr, "ERROR: %s" % error
			print >> sys.stderr, format_exc()
		except KeyboardInterrupt:
			mta.close()
			break

###
### Entry Point
###

if __name__ == "__main__":
	main()
