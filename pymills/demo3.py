
from time import time, sleep
from random import choice, random

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

def main():

	eventManager = EventManager()

	eventManager.addListener(listenerA, "test")
	eventManager.addListener(listenerB, "adder")
	eventManager.addListener(listenerC, "main")

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

			eventManager.sendEvent(event, "adder")

		eventManager.flushEvents()

		sleep(0.5)

if __name__ == "__main__":
	main()
