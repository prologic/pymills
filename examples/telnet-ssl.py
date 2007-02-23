#!/usr/bin/env python

from pymills.event import *
from pymills.sockets import TCPClient

class TelnetClient(TCPClient):

	@listener("connect")
	def onCONNECT(self, host, port):
		print "Connected to %s" % host
		print "Server: %s" % self.server
		print "Issuer: %s" % self.issuer
	
	@listener("read")
	def onREAD(self, line):
		print line

def main(host, port):

	import socket
	from pymills.io import SelectInput

	event = EventManager()
	client = TelnetClient(event, ssl=True)
	input = SelectInput()

	print "Trying %s..." % host
	client.open(host, int(port))

	while client.connected:
		client.process()
		event.flush()
		if input.poll():
			line = input.readline()
			client.write(line.strip() + "\r\n")
	event.flush()

if __name__ == "__main__":
	import sys

	if len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print "Usage: telnet.py host port"
