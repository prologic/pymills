#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills import event
from pymills.event import *

class HelloWorld(Component):

	@listener("hello")
	def onHELLO(self, message):
		print message
		self.push(Event("Received", message), "received")

def main():
	debugger.IgnoreEvents = ["Read", "Write"]
	bridge = Bridge(8000)

	event.manager += bridge + HelloWorld() + debugger

	while True:
		try:
			manager.flush()
			bridge.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
