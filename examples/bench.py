#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""Event Library Bench Marking Tool

Bench marking example. THis example does some simple
benchmaking of the event library. It's capable of
doing both local events and remote events and will
print out some statistics about each run.
"""

import math
import time
import hotshot
import optparse

import pymills
from pymills.event import listener, filter, \
		Component, Manager, Remote, Event
from pymills.misc import duration

USAGE = "%prog [options]"
VERSION = "%prog v" + pymills.__version__

ERRORS = [
		(0, "Cannot listen and connect at the same time!"),
		(1, "Invalid events spcified. Must be an integer."),
		(2, "Invalid time spcified. Must be an integer."),
		(3, "Invalid nthreads spcified. Must be an integer."),
		]

def parse_options():
	"""parse_options() -> opts, args

	Parse the command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-l", "--listen",
			action="store_true", default=False, dest="listen",
			help="Listen on 0.0.0.0:64000 (UDP) (test remote events)")
	parser.add_option("-c", "--connect",
			action="store", default=None, dest="connect",
			help="Connect to given host (test remote events)")
	parser.add_option("-t", "--time",
			action="store", default=0, dest="time",
			help="Stop after specified elapsed seconds")
	parser.add_option("-e", "--events",
			action="store", default=0, dest="events",
			help="Stop after specified number of events")
	parser.add_option("-p", "--profile",
			action="store_true", default=False, dest="profile",
			help="Enable execution profiling support")

	opts, args = parser.parse_args()

	try:
		opts.events = int(opts.events)
	except Exception, e:
		print str(e)
		parser.exit(ERRORS[1][0], ERRORS[1][1])

	try:
		opts.time = int(opts.time)
	except Exception, e:
		print str(e)
		parser.exit(ERRORS[2][0], ERRORS[2][1])

	if opts.listen and opts.connect is not None:
		parser.exit(ERRORS[0][0], ERRORS[0][1])

	return opts, args

class Sender(Component):

	@listener("received")
	def onRECEIVED(self, message=""):
		#print message
		self.event.push(Event(message="hello"), "hello")

class Receiver(Component):

	@listener("hello")
	def onHELLO(self, message=""):
		self.event.push(Event(message="Got: %s" % message),
				"received")

class State(Component):

	def __init__(self, event):
		self.done = False

	@listener("stop")
	def onSTOP(self):
		self.done = True

class Monitor(Component):

	def __init__(self, event):
		self._eventCount = 0

	def getEventCount(self):
		return self._eventCount

	@filter()
	def onDEBUG(self, *args, **kwargs):
		self._eventCount += 1
		return False

def main():

	opts, args = parse_options()

	nodes = []
	if opts.connect is not None:
		nodes = opts.connect.split(",")

	if opts.listen or opts.connect:
		event = Remote(nodes=nodes)
	else:
		event = Manager()
	monitor = Monitor(event)
	state = State(event)

	if opts.listen:
		receiver = Receiver(event)
	elif opts.connect:
		sender = Sender(event)
	else:
		sender = Sender(event)
		receiver = Receiver(event)

	sTime = time.time()

	if opts.profile:
		profiler = hotshot.Profile("bench.prof")
		profiler.start()

	event.push(Event(message="hello"), "hello")

	while not state.done:
		try:
			event.flush()
			if hasattr(event, "process"):
				event.process()

			if opts.events > 0 and monitor.getEventCount() > opts.events:
				event.send(Event(), "stop")
				break
			if opts.time > 0 and (time.time() - sTime) > opts.time:
				event.send(Event(), "stop")
				break

		except KeyboardInterrupt:
			event.send(Event(), "stop")
			break

	print

	eTime = time.time()

	tTime = eTime - sTime
	lTime = duration(tTime)

	print "Total Events: %d" % monitor.getEventCount()
	print "%d/s after %ds" % (
			int(math.ceil(float(monitor.getEventCount()) / tTime)),
			tTime)

	if opts.profile:
		profiler.stop()
		profiler.close()

		stats = hotshot.stats.load("bench.prof")
		stats.strip_dirs()
		stats.sort_stats("time", "calls")
		stats.print_stats(20)

if __name__ == "__main__":
	main()
