#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills import event
from pymills.event import manager
from pymills.net.sockets import TCPServer
from pymills.net.http import HTTP, Response
from pymills.event.core import listener, Component

###
### Components
###

class Test(Component):

	@listener("request")
	def onREQUEST(self, request, response):
		response.body = "Hello World!"
		self.send(Response(response), "response")

class WebServer(TCPServer, HTTP): pass

###
### Main
###

def main():
	server = WebServer(10000)
	event.manager += server
	event.manager += Test()

	while True:
		try:
			manager.flush()
			server.poll()
		except KeyboardInterrupt:
			break

###
### Entry Point
###

if __name__ == "__main__":
	main()
