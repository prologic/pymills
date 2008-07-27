#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import filter, listener, Manager, UnhandledEvent
from pymills.net.sockets import TCPServer

class Echo(TCPServer):

	@listener("read")
	def onREAD(self, sock, data):
		print "Data: %s" % data
		self.write(sock, data)
	
def main():
	e = Manager()
	echo = Echo(e, 8000)

	while True:
		try:
			e.flush()
			echo.poll()
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
