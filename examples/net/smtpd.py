#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import sys
from traceback import format_exc

from pymills.net.smtp import SMTP
from pymills.net.sockets import TCPServer
from pymills.event import listener, Manager

class SMTPServer(TCPServer, SMTP):

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
	def onQUIT(self, sock, error):
		print >> sys.stderr, "%s Error: %s" % (sock, error)

	@listener("message")
	def onMESSAGE(self, sock, mailfrom, rcpttos, data):
		print >> sys.stderr, "New Mail Message\n"
		print >> sys.stderr, "From: %s" % mailfrom
		print >> sys.stderr, "To: %s\n" % ",".join(rcpttos)

		for line in data:
			print >> sys.stderr, line

def main():
	manager = Manager()
	server = SMTPServer(manager, 1025)

	while True:
		try:
			server.process()
			manager.flush()
		except Exception, e:
			print >> sys.stderr, "ERROR: %s" % e
			print >> sys.stderr, format_exc()
		except KeyboardInterrupt:
			break
	manager.flush()

if __name__ == "__main__":
	main()
