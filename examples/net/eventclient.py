#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import time

from pymills import event
from pymills.event import *

class Foo(Component):

	@listener("received")
	def onRECEIVED(self, message):
		print "%s received" % message

def main():
	debugger.IgnoreEvents = ["Read", "Write"]
	bridge = Bridge(8001, nodes=[("127.0.0.1", 8000)])

	event.manager += bridge + debugger + Foo()

	sTime = time()

	while True:
		try:
			manager.flush()
			bridge.poll()
			if (time() - sTime) > 5:
				manager.push(Event("Hello", "hello"), "hello")
				sTime = time()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
