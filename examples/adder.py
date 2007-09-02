#!/usr/bin/env python

from pymills.event import listener, Component, \
		Event, Remote

class Adder(Component):

	@listener("add")
	def onADD(self, x, y):
		print "Adding %s + %s" % (x, y)
		r = x + y
		self.event.push(Event(r), "result")

def main():
	event = Remote(port=12000)
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
