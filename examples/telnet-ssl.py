#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.sockets import TCPClient
from pymills.event import listener, Manager

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

	from pymills.io import SelectInput

	event = Manager()
	client = TelnetClient(event)
	input = SelectInput()

	print "Trying %s..." % host
	client.open(host, int(port), ssl=True)

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
