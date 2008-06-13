#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import sys
from traceback import format_exc

from pymills.net.smtp import SMTP
from pymills.net.sockets import TCPServer
from pymills.event import listener, Manager

class SMTPServer(TCPServer, SMTP):
	pass

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
