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
		(1, "Cannot listen and connect at the same time!"),
		]

def parse_options():
	"""parse_options() -> opts, args

	Parse the command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-c", "--connect",
			action="store", default=None, dest="connect",
			help="Connect to given host (test remote events)")
	parser.add_option("-l", "--listen",
			action="store_true", default=False, dest="listen",
			help="Listen on 0.0.0.0:64000 (UDP) (test remote events)")

	opts, args = parser.parse_args()

	if opts.listen and opts.connect is not None:
		parser.exit(ERRORS[0][0], ERRORS[0][1])

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

	@listener("bar")
	def onBAR(self, event):

		self.count += 1

		self.event.push(
				Event(),
				self.event.getChannelID("bar"))

def main():

	opts, args = parse_options()

	if opts.listen:
		event = RemoteManager()
	else:
		if opts.connect is not None:
			print opts.connect
			nodes = [(x.split(":")[0], int(x.split(":")[1])) for x in opts.connect.split(",")]
			event = RemoteManager(nodes=nodes)
		else:
			event = EventManager()

	bench = Bench(event)

	if not opts.listen:
		event.push(
				Event(),
				event.getChannelID("foo"))
	else:
		event.push(
				Event(),
				event.getChannelID("bar"))

	sTime = time.time()

	if opts.listen or opts.connect is not None:
		while True:
			try:
				event.flush()
				event.process()
			except:
				break
	else:
		while True:
			try:
				event.flush()
			except:
				break
	
	eTime = time.time()

	tTime = eTime - sTime
	lTime = duration(tTime)

	print "Total Events: %d" % bench.count
	print "%d/s after %ds" % (bench.count / tTime, tTime)

if __name__ == "__main__":
	main()
