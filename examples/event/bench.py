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
from pymills.event import *
from pymills.misc import duration

USAGE = "%prog [options]"
VERSION = "%prog v" + pymills.__version__

ERRORS = [
		(0, "Cannot listen and connect at the same time!"),
		(1, "Invalid events spcified. Must be an integer."),
		(2, "Invalid time spcified. Must be an integer."),
		(3, "Invalid nthreads spcified. Must be an integer."),
		]

###
### Functions
###

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
	parser.add_option("-c", "--concurrency",
			action="store", type="int", default=1, dest="concurrency",
			help="Set concurrency level. (Default: 1)")
	parser.add_option("-t", "--time",
			action="store", type="int", default=0, dest="time",
			help="Stop after specified elapsed seconds")
	parser.add_option("-e", "--events",
			action="store", type="int", default=0, dest="events",
			help="Stop after specified number of events")
	parser.add_option("-p", "--profile",
			action="store_true", default=False, dest="profile",
			help="Enable execution profiling support")
	parser.add_option("-m", "--mode",
			action="store", default="sync", dest="mode",
			help="Operation mode (sync, tpuy). Default: sync")
	parser.add_option("-d", "--debug",
			action="store_true", default=False, dest="debug",
			help="Enable debug mode. (Default: False)")

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

	if opts.listen and args:
		parser.exit(ERRORS[0][0], ERRORS[0][1])

	return opts, args

###
### Events
###

class Stop(Event): pass
class Term(Event): pass
class Hello(Event): pass
class Received(Event): pass

###
### Components
###

class Sender(Component):

	concurrency = 1

	@listener("received")
	def onRECEIVED(self, message=""):
		self.push(Hello("hello"), "hello", self.channel)

class Receiver(Component):

	@listener("helo")
	def onHELO(self, address, port):
		self.send(Hello("hello"), "hello", self.channel)

	@listener("hello")
	def onHELLO(self, message=""):
		self.push(Received(message), "received", self.channel)

class Test(Component):

	@listener("hello")
	def onHELLO(self, message):
		self.push(Hello(message), "hello", self.channel)

class State(Component):

	done = False

	@listener("stop")
	def onSTOP(self):
		self.push(Term(), "term")

	@listener("term")
	def onTERM(self):
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
	def onEVENTS(self, event, *args, **kwargs):
		self.events += 1

###
### Main
###

def main():
	opts, args = parse_options()

	monitor = Monitor(e)
	state = State(e)

	debugger.set(opts.debug)

	if opts.listen or args:
		nodes = []
		if args:
			for node in args:
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

	if opts.mode.lower() == "tput":
		print "Setting up Test..."
		if opts.concurrency > 1:
			for c in xrange(int(opts.concurrency)):
				Test(e, channel=c)
		else:
			Test(e)
		monitor.sTime = time.time()
	elif opts.listen:
		print "Setting up Receiver..."
		if opts.concurrency > 1:
			for c in xrange(int(opts.concurrency)):
				Receiver(e, channel=c)
		else:
			Receiver(e)
	elif args:
		print "Setting up Sender..."
		if opts.concurrency > 1:
			for c in xrange(int(opts.concurrency)):
				Sender(e, channel=c)
		else:
			Sender(e)
	else:
		print "Setting up Sender..."
		print "Setting up Receiver..."
		if opts.concurrency > 1:
			for c in xrange(int(opts.concurrency)):
				Sender(e, channel=c)
				Receiver(e, channel=c)
		else:
			Sender(e)
			Receiver(e)
		monitor.sTime = time.time()

	if opts.profile:
		profiler = hotshot.Profile("bench.prof")
		profiler.start()

	if opts.concurrency > 1:
		for c in xrange(int(opts.concurrency)):
			e.push(Hello("hello"), "hello", c)
	else:
		e.push(Hello("hello"), "hello")

	while not state.done:
		try:
			e.flush()
			bridge.poll()

			if opts.events > 0 and monitor.events > opts.events:
				e.send(Stop(), "stop")
			if opts.time > 0 and (time.time() - monitor.sTime) > opts.time:
				e.send(Stop(), "stop")

		except KeyboardInterrupt:
			e.send(Stop(), "stop")

	print

	eTime = time.time()

	tTime = eTime - monitor.sTime

	print "Total Events: %d (%d/s after %0.2fs)" % (
			monitor.events, int(math.ceil(float(monitor.events) / tTime)), tTime)

	if opts.profile:
		profiler.stop()
		profiler.close()

		stats = hotshot.stats.load("bench.prof")
		stats.strip_dirs()
		stats.sort_stats("time", "calls")
		stats.print_stats(20)

###
### Entry Point
###

if __name__ == "__main__":
	main()
