#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, Manager
from pymills.net.sockets import UDPServer

class EchoServer(UDPServer):

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		print "New connection: %s:%d" % (host, port)
		self.write(sock, "Ready\r\n")

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		print "Disconnection: %s" % sock

	@listener("read")
	def onREAD(self, sock, line):
		print "%s: %s" % (sock, line)
		print dir(sock)
		self.write(sock, line + "\r\n")

def main():
	e = Manager()
	server = EchoServer(e, 1234)

	while True:
		try:
			server.process()
			e.flush()
		except KeyboardInterrupt:
			break
	e.flush()

if __name__ == "__main__":
	main()
