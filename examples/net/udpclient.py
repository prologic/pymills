#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import readline

from pymills import event
from pymills.event import *
from pymills.net.sockets import UDPClient

class UDPClient(UDPClient):

	@listener("connect")
	def onCONNECT(self, host, port):
		print "Connected to %s" % host

	@listener("read")
	def onREAD(self, line):
		line = line.strip()
		print line

def main(host, port):

	client = UDPClient()
	event.manager += client

	print "Trying %s..." % host
	client.open(host, int(port))

	while client.connected:
		manager.flush()
		client.poll()
		line = raw_input().strip()
		client.write("%s\n" % line)

if __name__ == "__main__":
	import sys

	if len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print "Usage: udpclient.py host port"
