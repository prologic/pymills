#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, Component, Manager, \
		Event

class InfiniteLoop(Component):

	@listener("foo")
	def onFOO(self, event):
		self.event.push(Event(), "foo")

def main():

	event = Manager()

	infiniteLoop = InfiniteLoop(event)

	event.push(Event(), "foo")

	while True:
		event.flush()

if __name__ == "__main__":
	main()
