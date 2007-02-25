#!/usr/bin/env python

from pymills.event import *

class HelloWorld(Component):

	@listener("hello")
	def onHELLO(self, event, message=""):
		print message
		self.event.push(Event(message), "received")

def main():
	event = RemoteManager()
	helloWorld = HelloWorld(event)

	while True:
		try:
			event.flush()
			event.process()
		except KeyboardInterrupt:
			break
	event.flush()

if __name__ == "__main__":
	main()
