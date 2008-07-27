#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import *

class HelloWorld(Component):

	@listener("hello")
	def onHELLO(self, message):
		print message
		self.push(Event("Received", message), "received")

def main():
	debugger.IgnoreEvents = ["Read", "Write"]
	bridge = Bridge(e, port=8000)
	HelloWorld(e)

	while True:
		try:
			e.flush()
			bridge.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
