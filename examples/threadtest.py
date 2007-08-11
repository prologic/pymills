#!/usr/bin/env python

import threading
from time import sleep

from pymills.event import listener, filter, Component, \
		Worker, Event, RemoteManager

class ThreadOne(Worker):

	@listener("hello")
	def onHELLO(self, event, message=""):
		self.event.push(Event("hello from 1 (%s)" % message), "received")
	
	def run(self):
		while self.isRunning():
			try:
				self.event.push(Event(message="foo!"), "hello")
				sleep(0.001)
			except KeyboardInterrupt:
				self.stop()

class ThreadTwo(Worker):

	@listener("hello")
	def onHELLO(self, event, message=""):
		self.event.push(Event("hello from 2 (%s)" % message), "received")

	def run(self):
		while self.isRunning():
			try:
				self.event.push(Event(message="bar!"), "hello")
				sleep(0.001)
			except KeyboardInterrupt:
				self.stop()

class Master(Component):

	@filter()
	def onDEBUG(self, event):
		print "DEBUG: %s" % event
		return False, event

	@listener("received")
	def onRECEIVED(self, event, message=""):
		print message

def main():
	event = RemoteManager()
	one = ThreadOne(event)
	two = ThreadTwo(event)
	master = Master(event)

	while True:
		try:
			event.flush()
			event.push(Event(message="Hello!"), "hello")
			sleep(0.001)
		except KeyboardInterrupt:
			break

	one.stop()
	two.stop()

	event.flush()

if __name__ == "__main__":
	main()
