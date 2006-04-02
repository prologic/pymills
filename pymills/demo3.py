
from time import time, sleep
from random import choice, random, seed

import event
from event import Event
from event import EventManager

def listenerA(event):

	print "Listener A:"

	for k, v in event.__dict__.iteritems():
		print " %s: %s" % (k, v)

def listenerB(event):

	print "Listener B:"

	x = getattr(event, "x")
	y = getattr(event, "y")
	op = getattr(event, "op")

	if op == "+":
		r = x + y
	elif op == "-":
		r = x - y
	elif op == "*":
		r = x * y
	elif op == "/":
		r = x / y

	print " %0.2f %s %0.2f = %0.2f" % (x, op, y, r)

def listenerC(event):

	tick = getattr(event, "tick", ".")
	print tick

	quit = getattr(event, "quit", False)
	if quit:
		raise SystemExit, 0

class Tester:

	def __init__(self, eventMander):
		self._eventMander = eventMander

		self.x = 0.0
	
	def pushEvent(self, event, channel):
		eventMander = self._eventMander
		eventMander.pushEvent(event, channel, self)
	
	def handleEvent(self, event):

		x = getattr(event, "x", 0.0)

		if self.x < 100.0:
			self.x += x

			if self.x > 100.0:
				event = Event()
				event.msg = "Success!"
				self.pushEvent(event, "test")
				event = Event()
				event.quit = True
				self.pushEvent(event, "main")
		
def foo(evt):
	print "foo"
#	return event.DISCARD
	if choice(range(0, 2)) == 0:
		return event.DISCARD
	else:
		evt.foo = "..."

def bar(event):
	print "bar"

def main():

	seed()

	eventManager = EventManager()

	tester = Tester(eventManager)

	eventManager.addListener(listenerA, "test")
	eventManager.addListener(listenerB, "calc")
	eventManager.addListener(listenerC, "main")

	eventManager.addListener(tester.handleEvent, "calc")

	eventManager.addFilter(foo, "test")
	eventManager.addListener(bar, "test")

	while True:

		event = Event()
		event.tick = time()

		eventManager.pushEvent(event, "main")

		if choice(range(0, 4)) == 0:

			event = Event()
			event.foo = "bar"

			eventManager.sendEvent(event, "test")

		if choice(range(0, 6)) == 0:

			event = Event()
			event.x = choice(range(0, 100)) * random()
			event.op = choice(["+", "-", "*", "/"])
			event.y = choice(range(0, 100)) * random()

			eventManager.sendEvent(event, "calc")
			eventManager.pushEvent(event, "calc")

		eventManager.flushEvents()

		sleep(0.5)

if __name__ == "__main__":
	main()
