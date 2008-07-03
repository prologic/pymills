#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.net.http import HTTP
from pymills.net.sockets import TCPServer
from pymills.event import listener, UnhandledEvent, Manager

class WebServer(TCPServer, HTTP):

	@listener("get")
	def onGET(self, req):
		return "OK"

def main():
	e = Manager()
	server = WebServer(e, 8000)

	while True:
		try:
			server.process()
			e.flush()
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break
	e.flush()

if __name__ == "__main__":
	main()
