#!/usr/bin/env python

from pymills.event import listener, filter, Component, \
		Event, RemoteManager

class Calc(Component):

	@filter()
	def onDEBUG(self, event):
		print "DEBUG: %s" % event
		return False, event

	@listener("result")
	def onRESULT(self, event, r):
		print "Result: %s" % r

def main():

	nodes = (
			"202.63.43.98",
			)

	event = RemoteManager(nodes)
	calc = Calc(event)

	x = float(raw_input("x: "))
	y = float(raw_input("y: "))

	event.push(Event(x, y), "add")

	event.flush()
	event.process()

if __name__ == "__main__":
	main()
