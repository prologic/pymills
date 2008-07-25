#!/usr/bin/env python

import sys

from pymills.event import filter, listener, Component, Event, Manager, Bridge

class Sniffer(Component):

	@filter()
	def onEVENTS(self, event, *args, **kwargs):
		print >> sys.stderr, event

def main():
	e = Manager()
	sniffer = Sniffer(e)
	bridge = Bridge(e)

	while True:
		try:
			e.flush()
			bridge.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
