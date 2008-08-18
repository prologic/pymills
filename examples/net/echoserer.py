#!/usr/bin/env python

from pymills import event
from pymills.event import *
from pymills.net.sockets import TCPServer

class Echo(TCPServer):

	@listener("read")
	def onREAD(self, sock, data):
		self.write(sock, data)
	
def main():
	echo = Echo(8000)
	event.manager += echo

	while True:
		try:
			manager.flush()
			echo.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
