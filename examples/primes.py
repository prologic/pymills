#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""Prime Number Finder

A Distributed Event Driven Prime Number Finder as an
example of how to use the pymills Event Library to
accomplish Distributed and Event Driven Programming.
"""

import math
import time
import optparse

import pymills
from pymills.misc import duration
from pymills.datatypes import Queue
from pymills.event import listener, filter, \
		Worker, Remote, Event, FilterEvent

USAGE = "%prog [options]"
VERSION = "%prog v" + pymills.__version__

ERRORS = [
		(0, "Invalid primes spcified. Must be an integer."),
		(1, "Invalid time spcified. Must be an integer."),
		]

def parse_options():
	"""parse_options() -> opts, args

	Parse the command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-c", "--connect",
			action="store", default=None, dest="connect",
			help="Connect to given host)")
	parser.add_option("-t", "--time",
			action="store", default=0, dest="time",
			help="Stop after specified elapsed seconds")
	parser.add_option("-p", "--primes",
			action="store", default=0, dest="primes",
			help="Stop after specified number of primes found")

	opts, args = parser.parse_args()

	try:
		opts.primes = int(opts.primes)
	except Exception, e:
		print str(e)
		parser.exit(ERRORS[0][0], ERRORS[0][1])

	try:
		opts.time = int(opts.time)
	except Exception, e:
		print str(e)
		parser.exit(ERRORS[1][0], ERRORS[1][1])

	return opts, args

def isPrime(n):

	if n == 2:
		return True

	for x in xrange(2, (n - 1)):
		if n % x == 0:
			return False
	
	return True

def getPrimes(s, e):
	primes = []
	for x in xrange(s, e):
		if isPrime(x):
			primes.append(x)
	return primes

class State(Worker):

	def __init__(self, *args, **kwargs):
		super(State, self).__init__(*args, **kwargs)

		self.done = False

	@listener("stop")
	def onSTOP(self):
		self.done = True

class Monitor(Worker):

	def __init__(self, *args, **kwargs):
		super(Monitor, self).__init__(*args, **kwargs)

		self._allPrimes = []
		self._myPrimes = []
		self._primesFound = 0

	def getAllPrimes(self):
		return self._allPrimes

	def getMyPrimes(self):
		return self._myPrimes

	def getPrimesFound(self):
		return self._primesFound

	@listener("NewPrime")
	def onNEWPRIME(self, event, prime):
		print "New Prime Found %d from %s" % (prime, event._source)
		self._primesFound += 1

class QueueManager(Worker):

	def __init__(self, *args, **kwargs):
		super(QueueManager, self).__init__(*args, **kwargs)

		self._queue = Queue(10)
	
	@filter("start")
	def onSTART(self):
		n = 0
		while not self._queue.full():
			self._queue.push(n)
			n += 1
		self.push(Event(), "checkq")
		raise FilterEvent

	@listener("checkq")
	def onCHECKQ(self):
		self.push(Event(n=self._queue.pop()), "check")
		self._queue.push(self._queue.bottom() + 1)

class PrimeFinder(Worker):

	def __init__(self, *args, **kwargs):
		super(PrimeFinder, self).__init__(*args, **kwargs)

	@listener("check")
	def onCHECK(self, n):
		if isPrime(n):
			self.push(Event(prime=n), "NewPrime")
		self.push(Event(), "checkq")

def main():

	opts, args = parse_options()

	nodes = []
	if opts.connect is not None:
		nodes = opts.connect.split(",")

	manager = Remote(nodes=nodes)
	monitor = Monitor(manager)
	state = State(manager)

	if opts.connect is None:
		QueueManager(manager)

	PrimeFinder(manager)

	sTime = time.time()

	manager.push(Event(), "start")

	while not state.done:
		try:
			manager.flush()
			manager.process()

			if opts.primes > 0 and monitor.getPrimesFound() > opts.primes:
				manager.send(Event(), "stop")
				break
			if opts.time > 0 and (time.time() - sTime) > opts.time:
				manager.send(Event(), "stop")
				break

		except KeyboardInterrupt:
			manager.send(Event(), "stop")
			break

	print

	eTime = time.time()

	tTime = eTime - sTime
	lTime = duration(tTime)

	print "Total Primes Found: %d" % monitor.getPrimesFound()
	print "%d/s after %ds" % (
			int(math.ceil(float(monitor.getPrimesFound()) / tTime)),
			tTime)

if __name__ == "__main__":
	main()
