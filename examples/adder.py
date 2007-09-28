#!/usr/bin/env python

from pymills.event import listener, Component, \
		Event, Remote

class Adder(Component):

	@listener("add")
	def onADD(self, x, y):
		print "Adding %s + %s" % (x, y)
		r = x + y
		self.push(Event(r), "result")

def main():
	e = Remote(port=12000)
	adder = Adder(e)

	while True:
		try:
			e.flush()
			e.process()
		except KeyboardInterrupt:
			break
	e.flush()

if __name__ == "__main__":
	main()
