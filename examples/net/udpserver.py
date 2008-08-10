#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills import event
from pymills.event import *
from pymills.net.sockets import UDPServer

class EchoServer(UDPServer):

	@listener("connect")
	def onCONNECT(self, sock, host, port):
		print "New connection: %s:%d" % (host, port)

	@listener("disconnect")
	def onDISCONNECT(self, sock):
		print "Disconnection: %s" % sock

	@listener("read")
	def onREAD(self, sock, line):
		line = line.strip()
		print "%s: %s" % (sock, line)
	
	@listener("error")
	def onERROR(self, sock, msg):
		print "ERROR (%s): %s" % (sock, msg)

def main():
	server = EchoServer(1234)
	event.manager += server

	while True:
		try:
			manager.flush()
			server.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
