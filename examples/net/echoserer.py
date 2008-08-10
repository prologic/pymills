#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills import event
from pymills.event import *
from pymills.net.sockets import TCPServer

class Echo(TCPServer):

	@listener("read")
	def onREAD(self, sock, data):
		print "Data: %s" % data
		self.write(sock, data)
	
def main():
	echo = Echo(8000)
	event.manager += echo

	while True:
		try:
			manager.flush()
			echo.poll()
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
