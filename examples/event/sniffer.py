#!/usr/bin/env python

from pymills.event import filter, listener, Component, \
		Event, Remote

class Sniffer(Component):

	@filter()
	def onDEBUG(self, event):
		print event

def main():
	e = Remote(nodes=("0.0.0.0:64000",), port=12000)
	sniffer = Sniffer(e)

	e.send(Event(), "")

	while True:
		try:
			e.flush()
			e.process()
		except KeyboardInterrupt:
			break
	e.flush()

if __name__ == "__main__":
	main()
