#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.net.sockets import TCPServer
from pymills.event import filter, listener, Manager, UnhandledEvent

class EchoServer(TCPServer):

	@filter()
	def onDEBUG(self, event, *args, **kwargs):
		print event

	@listener("read")
	def onREAD(self, sock, data):
		self.write(sock, data)
	
def main():
	e = Manager()
	server = EchoServer(e, 8000)

	while True:
		try:
			e.flush()
			server.poll()
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
