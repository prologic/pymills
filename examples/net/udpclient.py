#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import readline

from pymills.net.sockets import UDPClient
from pymills.event import listener, Manager

class UDPClient(UDPClient):

	@listener("connect")
	def onCONNECT(self, host, port):
		print "Connected to %s" % host

	@listener("read")
	def onREAD(self, line):
		line = line.strip()
		print line

def main(host, port):

	event = Manager()
	client = UDPClient(event)

	print "Trying %s..." % host
	client.open(host, int(port))

	while client.connected:
		client.process()
		event.flush()
		line = raw_input().strip()
		client.write("%s\n" % line)
	event.flush()

if __name__ == "__main__":
	import sys

	if len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print "Usage: udpclient.py host port"
