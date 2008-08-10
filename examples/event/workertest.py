#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep

from pymills import event
from pymills.event import *

class WorkerOne(Worker):

	@listener("hello")
	def onHELLO(self, message):
		self.push(
			Event("Received", "Hello from %s received: %s" % (self, message)),
			"received")

	def run(self):
		while self.isRunning():
			try:
				self.push(Event("Hello", message="Hello from %s" % self), "hello")
				sleep(1)
			except KeyboardInterrupt:
				self.stop()

class WorkerTwo(Worker):

	@listener("hello")
	def onHELLO(self, message):
		self.push(
			Event("Received", "Hello from %s received: %s" % (self, message)),
			"received")

	def run(self):
		while self.isRunning():
			try:
				self.push(Event("Hello", message="Hello from %s" % self), "hello")
				sleep(1)
			except KeyboardInterrupt:
				self.stop()

class Master(Component):

	@listener("received")
	def onRECEIVED(self, message):
		print message

def main():
	event.manager += Master()
	event.manager += WorkerOne(start=True)
	event.manager += WorkerTwo(start=True)

	while True:
		try:
			manager.flush()
			manager.push(Event("Hello", "Hello!"), "hello")
			sleep(1)
		except KeyboardInterrupt:
			break

	for worker in workers():
		worker.stop()

if __name__ == "__main__":
	main()
