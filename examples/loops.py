#!/usr/bin/env python

from pymills.event import *

class InfiniteLoop(Component):

	@listener("foo")
	def onFOO(self, event):
		self.event.push(
				Event(),
				self.event.getChannelID("foo"),
				self)

def main():

	event = EventManager()

	infiniteLoop = InfiniteLoop(event)

	event.push(
			Event(),
			event.getChannelID("foo"),
			None)

	while True:
		event.flush()

if __name__ == "__main__":
	main()
