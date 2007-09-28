#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep

from pymills.event import listener, filter, Component, \
		Worker, Event, Manager

class ThreadOne(Worker):

	@listener("hello")
	def onHELLO(self, event, message=""):
		self.push(Event("hello from 1 (%s)" % message), "received")

	def run(self):
		while self.isRunning():
			try:
				self.push(Event(message="foo!"), "hello")
				sleep(0.001)
			except KeyboardInterrupt:
				self.stop()

class ThreadTwo(Worker):

	@listener("hello")
	def onHELLO(self, event, message=""):
		self.push(Event("hello from 2 (%s)" % message), "received")

	def run(self):
		while self.isRunning():
			try:
				self.push(Event(message="bar!"), "hello")
				sleep(0.001)
			except KeyboardInterrupt:
				self.stop()

class Master(Component):

	@filter()
	def onDEBUG(self, event):
		print "DEBUG: %s" % event

	@listener("received")
	def onRECEIVED(self, event, message=""):
		print message

def main():
	e = Manager()
	one = ThreadOne(e)
	two = ThreadTwo(e)
	master = Master(e)

	while True:
		try:
			e.flush()
			e.push(Event(message="Hello!"), "hello")
			sleep(0.001)
		except KeyboardInterrupt:
			break

	one.stop()
	two.stop()

	e.flush()

if __name__ == "__main__":
	main()
