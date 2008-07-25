#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""Prime Number Finder

A distributed prime number finder example.
"""

import sys
import math
import time
import optparse
from time import sleep
from uuid import uuid1 as uuid

import pymills
from pymills.misc import duration

from pymills.event import Event
from pymills.event import FilterEvent
from pymills.event import listener, filter
from pymills.event import DummyBridge, Bridge
from pymills.event import Component, Manager, Debugger

USAGE = "%prog [options] [host:[port]]"
VERSION = "%prog v" + pymills.__version__

###
### Functions
###

def parse_options():
	"""parse_options() -> opts, args

	Parse the command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-o", "--output",
			action="store", type="str", default="primes.txt", dest="output",
			help="Output filename to write primes. (Default: primes.txt)")
	parser.add_option("-s", "--slave",
			action="store_true", default=False, dest="slave",
			help="Slave mode (gets tasks from a master) (Default: False)")
	parser.add_option("-b", "--bind",
			action="store", type="str", default="0.0.0.0", dest="bind",
			help="Bind to address:[port] (UDP) (test remote events)")
	parser.add_option("-t", "--time",
			action="store", type="int", default=0, dest="time",
			help="Stop after specified elapsed seconds")
	parser.add_option("-p", "--primes",
			action="store", type="int", default=0, dest="primes",
			help="Stop after specified number of primes have been found.")
	parser.add_option("-d", "--debug",
			action="store_true", default=False, dest="debug",
			help="Enable debug mode. (Default: False)")

	opts, args = parser.parse_args()

	return opts, args

###
### Events
###

class Start(Event): pass
class Stop(Event): pass
class Query(Event): pass

class Busy(Event):

	def __init__(self, id):
		super(Busy, self).__init__(id)

class Ready(Event):

	def __init__(self, id):
		super(Ready, self).__init__(id)

class Task(Event):

	def __init__(self, id, n):
		super(Task, self).__init__(id, n)

class Run(Event):

	def __init__(self, id, n):
		super(Run, self).__init__(id, n)

class Done(Event):

	def __init__(self, id, n, r):
		super(Done, self).__init__(id, n, r)

class Task(Event):

	def __init__(self, id, n):
		super(Task, self).__init__(id, n)

class Prime(Event):

	def __init__(self, n):
		super(Prime, self).__init__(n)

###
### Components
###

class PrimeFinder(Component):

	id = uuid()
	primes = 0

	busy = False
	n = None
	start = None
	stop = None
	step = None
	
	def reset(self):
		self.busy = False
		self.n = None
		self.start = None
		self.stop = None
		self.step = None

	@listener("query")
	def onQUERY(self):
		if self.busy:
			self.push(Busy(self.id), "busy")
		else:
			self.push(Ready(self.id), "ready")

	@listener("task")
	def onTASK(self, id, n):
		if self.busy:
			self.push(Busy(self.id), "busy")
			return
		elif not id == self.id:
			# Not our task
			return
		else:
			self.busy = True
	
		# Ensure n is a positive integer
		self.n = abs(int(n))

		if n < 2:
			# 0 and 1 are not primes
			self.reset()
			self.push(Done(self.id, n, False), "done")
			return
		elif n == 2:
			# 2 is the only even prime
			self.reset()
			self.primes += 1
			self.push(Done(self.id, n, True), "done")
			return
		elif not n & 1:
			# all other even numbers are not primes
			self.reset()
			self.push(Done(self.id, n, False), "done")
			return
		else:
			# range starts at 3 and increments by the squareroot of n
			# for all odd numbers.

			self.start = 3
			self.stop = int(self.n**0.5) + 1
			self.step = 2

			self.push(Run(self.id, self.n), "run")
	
	@listener("run")
	def onRUN(self, id, n):
		if self.start % self.n == 0:
			self.push(Done(self.id, self.n, False), "done")
			self.reset()
		else:
			self.start += self.step
			if self.start > self.stop:
				self.primes += 1
				self.push(Done(self.id, self.n, True), "done")
				self.reset()
			else:
				self.push(Run(self.id, self.n), "run")

class TaskManager(Component):

	n = 999
	primes = []

	jobs = {}

	@listener("start")
	def onSTART(self):
		self.push(Query(), "query")

	@listener("ready")
	def onREADY(self, id):
		self.jobs[id] = self.n
		self.push(Task(id, self.n), "task")
		self.n += 1

#	@listener("busy")
#	def onBUSY(self, id):
#		self.push(Query(), "query")

	@listener("done")
	def onDONE(self, id, n, r):
		self.jobs[id] = None
		if r and (n not in self.primes):
			self.primes.append(n)
			self.push(Prime(n), "prime")
		self.push(Query(), "query")

###
### Management Components
###

class State(Component):

	done = False
	n = 0
	N = 1

	@listener("helo")
	def onHELO(self, host, port):
		self.N += 1

	@listener("stop")
	def onSTOP(self):
		if self.n < self.N:
			self.push(Event(), "stop")
			self.n += 1
		else:
			self.done = True

class Stats(Component):

	sTime = time.time()
	events = 0
	primes = 0
	state = 0

	@filter()
	def onEVENTS(self, event, *args, **kwargs):
		self.events += 1

	@filter("prime")
	def onPRIME(self, n):
		self.primes += 1

###
### Main
###

def main():

	opts, args = parse_options()

	e = Manager()
	stats = Stats(e)
	state = State(e)

	if opts.debug:
		debugger = Debugger(e)
		debugger.IgnoreChannels.extend(["read", "write"])

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
	bridge.IgnoreEvents.append(Run)
	if not opts.slave:
		bridge.IgnoreEvents.extend([Ready, Busy, Done, Prime])

	finder = PrimeFinder(e)

	if not opts.slave:
		taskman = TaskManager(e)
		e.push(Start(), "start")

	while not state.done:
		try:
			e.flush()
			bridge.poll()
			#sleep(1)

			if opts.primes > 0 and stats.primes > opts.primes:
				e.send(Stop(), "stop")
			if opts.time > 0 and (time.time() - stats.sTime) > opts.time:
				e.send(Stop(), "stop")

		except KeyboardInterrupt:
			e.send(Stop(), "stop")

	print

	eTime = time.time()

	tTime = eTime - stats.sTime

	print "I found %d primes (%d/s after %0.2fs)" % (
			finder.primes, int(math.ceil(float(finder.primes) / tTime)), tTime)

	if not opts.slave:

		print "Total Primes: %d (%d/s after %0.2fs)" % (
				stats.primes, int(math.ceil(float(stats.primes) / tTime)), tTime)
		print "Total Events: %d (%d/s after %0.2fs)" % (
				stats.events, int(math.ceil(float(stats.events) / tTime)), tTime)

		fd = open(opts.output, "w")
		for prime in taskman.primes:
			fd.write("%d\n" % prime)
		fd.close()

###
### Entry Point
###

if __name__ == "__main__":
	main()
