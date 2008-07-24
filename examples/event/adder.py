#!/usr/bin/env python

from pymills.event import listener, Component, Event, Manager, Bridge

class Adder(Component):

	@listener("add")
	def onADD(self, x, y):
		print "Adding %s + %s" % (x, y)
		r = x + y
		self.push(Event(r), "result")

def main():
	e = Manager()
	bridge = Bridge(e, port=9000)
	Adder(e)

	while True:
		try:
			e.flush()
			bridge.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
