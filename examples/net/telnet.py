#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.net.sockets import TCPClient
from pymills.event import listener, Manager, UnhandledEvent

class TelnetClient(TCPClient):

	@listener("connect")
	def onCONNECT(self, host, port):
		print "Connected to %s" % host

	@listener("read")
	def onREAD(self, line):
		print line

def main(host, port):

	from pymills.io import SelectInput

	e = Manager()
	client = TelnetClient(e)
	input = SelectInput()

	print "Trying %s..." % host
	client.open(host, int(port))

	while client.connected:
		try:
			client.process()
			e.flush()
			if input.poll():
				line = input.readline()
				client.write(line.strip() + "\r\n")
		except UnhandledEvent:
			pass
		except KeyboardInterrupt:
			break
	client.close()
	try:
		e.flush()
	except UnhandledEvent:
		pass

if __name__ == "__main__":
	import sys

	if len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print "Usage: telnet.py host port"
