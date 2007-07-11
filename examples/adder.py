#!/usr/bin/env python

from pymills.event import listener, filter, Component, \
		Event, RemoteManager

class Adder(Component):

	@filter()
	def onDEBUG(self, event):
		print "DEBUG: %s" % event
		return False, event

	@listener("add")
	def onADD(self, event, x, y):
		print "Adding %s + %s" % (x, y)
		r = x + y
		self.event.push(Event(r), "result")

def main():
	event = RemoteManager()
	adder = Adder(event)

	while True:
		try:
			event.flush()
			event.process()
		except KeyboardInterrupt:
			break
	event.flush()

if __name__ == "__main__":
	main()
