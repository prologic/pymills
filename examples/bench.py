#!/usr/bin/env python
# Filename: bench.py
# Module:   bench
# Date:     25 February 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""bench

Bench marking example. THis example does some simple
benchmaking of the event library. It's capable of
doing both local event and remote events and will
print out some statistics about each run.
"""

__description__ = "pymills.event bench marking"
__version__ = "0.1.0"
__author__ = "James Mills"
__author_email__ = "James Mills, prologic at shortcircuit dot net dot au"
__url__ = "http://trac.shortcircuit.net.au/pymills/"
__copyright__ = "CopyRight (C) 2005 by James Mills"
__license__ = "GPL"

import time
import optparse

from pymills.event import *
from pymills.misc import duration

USAGE = "%prog [options]"
VERSION = "%prog v" + __version__

ERRORS = [
#		(1, "Cannot listen and connect at the same time!"),
		(1, "Invalid events spcified. Must be an integer."),
		(2, "Invalid time spcified. Must be an integer."),
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

#	if opts.listen and opts.connect is not None:
#		parser.exit(ERRORS[0][0], ERRORS[0][1])

	return opts, args

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

	opts, args = parse_options()

	nodes = []
	if opts.connect is not None:
		nodes = opts.connect.split(",")

	if opts.listen:
		event = RemoteManager(nodes=nodes)
	else:
		event = EventManager()

	bench = Bench(event)

	event.push(Event(), "foo")

	sTime = time.time()

	while True:
		try:
			event.flush()
			if hasattr(event, "process"):
				event.process()

			if opts.events > 0 and bench.count > opts.events:
				break
			if opts.time > 0 and (time.time() - sTime) > opts.time:
				break
		except:
			break
	
	eTime = time.time()

	tTime = eTime - sTime
	lTime = duration(tTime)

	print "Total Events: %d" % bench.count
	print "%d/s after %ds" % (bench.count / tTime, tTime)

if __name__ == "__main__":
	main()
