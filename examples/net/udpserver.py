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
		line = line.strip()
		print "%s: %s" % (sock, line)
		self.write(sock, "%s\n" % line)
	
	@listener("error")
	def onERROR(self, sock, msg):
		print "ERROR (%s): %s" % (sock, msg)

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
