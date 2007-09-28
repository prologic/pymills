#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pprint import pprint

from pymills.net.http import HTTP
from pymills.net.sockets import TCPServer
from pymills.event import filter, listener, Manager, \
		FilterEvent

class WebServer(TCPServer, HTTP):

	@filter()
	def onDEBUG(self, event):
		print event

def main():
	e = Manager()
	server = WebServer(e, 9000)

	pprint(e.getHandlers())

	while True:
		try:
			server.process()
			e.flush()
		except KeyboardInterrupt:
			break
	e.flush()

if __name__ == "__main__":
	main()
