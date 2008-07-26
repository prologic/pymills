#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import math
from time import time

from pymills.event import listener, Component, Manager, Event

class Loop(Component):

	events = 0

	@listener("foo")
	def onFOO(self, event):
		self.events += 1
		self.push(Event("Loop"), "foo")

def main():
	e = Manager()
	loop = Loop(e)

	e.push(Event("Test"), "foo")

	sTime = time()

	while True:
		try:
			e.flush()
		except KeyboardInterrupt:
			break

	eTime = time()
	tTime = eTime - sTime

	print "Total Events: %d (%d/s after %0.2fs)" % (
			loop.events, int(math.ceil(float(loop.events) / tTime)), tTime)

if __name__ == "__main__":
	main()
