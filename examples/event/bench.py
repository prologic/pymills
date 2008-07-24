#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""Event Library Bench Marking Tool

Bench marking example. THis example does some simple
benchmaking of the event library. It's capable of
doing both local events and remote events and will
print out some statistics about each run.
"""

import sys
import math
import time
import hotshot
import optparse
import hotshot.stats

import pymills
from pymills.misc import duration
from pymills.event import listener, filter, Component, Manager, Bridge, Event

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
			help="Listen on 0.0.0.0:8000 (UDP) (test remote events)")
	parser.add_option("-b", "--bind",
			action="store", default="0.0.0.0", dest="bind",
			help="Bind to address:[port] (UDP) (test remote events)")
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
	parser.add_option("-m", "--mode",
			action="store", default="sync", dest="mode",
			help="Change operation mode (sync, tput). Default: sync")

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
		self.push(Event(message="hello"), "hello")

class Receiver(Component):

	@listener("helo")
	def onHELO(self, address, port):
		self.send(Event("hello"), "hello")

	@listener("hello")
	def onHELLO(self, message=""):
		self.push(Event(message="Got: %s" % message), "received")

class State(Component):

	done = False
	n = 0

	@listener("stop")
	def onSTOP(self):
		if self.n < 2:
			self.push(Event(), "stop")
			self.n += 1
		else:
			self.done = True

class Monitor(Component):

	sTime = sys.maxint
	events = 0
	state = 0

	@listener("helo")
	def onHELO(self, *args, **kwargs):
		print "Resetting sTime"
		self.sTime = time.time()

	@filter()
	def onDEBUG(self, event, *args, **kwargs):
		self.events += 1

class DummyBridge(object):

	def poll(self):
		pass

def main():

	opts, args = parse_options()

	e = Manager()

	if opts.listen or opts.connect:

		nodes = []
		if opts.connect is not None:
			for node in opts.connect.split(","):
				if ":" in node:
					host, port = node.split(":")
					port = int(port)
				else:
					host = node
					port = 8000
				nodes.append((host, port))

		if opts.bind is not None:
			if ":" in opts.bind:
				address, port = opts.bind.split(":")
				port = int(port)
			else:
				address, port = opts.bind, 8000

		bridge = Bridge(e, port=port, address=address, nodes=nodes)
	else:
		bridge = DummyBridge()

	monitor = Monitor(e)
	state = State(e)

	if opts.listen:
		print "Setting up Receiver..."
		Receiver(e)
	elif opts.connect:
		print "Setting up Sender..."
		Sender(e)
	else:
		print "Setting up Sender..."
		print "Setting up Receiver..."
		Sender(e)
		Receiver(e)
		monitor.sTime = time.time()

	if opts.profile:
		profiler = hotshot.Profile("bench.prof")
		profiler.start()

	e.send(Event("hello"), "hello")

	while not state.done:
		try:
			e.flush()
			bridge.poll()

			if opts.events > 0 and monitor.events > opts.events:
				e.send(Event(), "stop")
			if opts.time > 0 and (time.time() - monitor.sTime) > opts.time:
				e.send(Event(), "stop")

		except KeyboardInterrupt:
			e.send(Event(), "stop")

	print

	eTime = time.time()

	tTime = eTime - monitor.sTime

	print "Total Events: %d" % monitor.events
	print "%d/s after %0.2fs" % (
			int(math.ceil(float(monitor.events) / tTime)),
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
