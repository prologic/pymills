#!/usr/bin/env python

import time

from pymills.event import *
from pymills.misc import duration

class Bench(Component):

	def __init__(self, event):
		self.count = 0

	@filter()
	def onDEBUG(self, event):
		return False, event

	@listener("foo")
	def onFOO(self, event):

		self.count += 1

		self.event.push(
				Event(),
				self.event.getChannelID("foo"))

def main():

	event = EventManager()
	bench = Bench(event)

	event.push(
			Event(),
			event.getChannelID("foo"))

	stime = time.time()

	while True:
		try:
			event.flush()
		except:
			break
	
	etime = time.time()

	ttime = etime - stime
	ltime = duration(ttime)

	print "Total Events: %d" % bench.count
	print "%d/s after %ds" % (bench.count / ttime, ttime)

if __name__ == "__main__":
	main()
