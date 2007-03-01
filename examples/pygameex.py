#!/usr/bin/env python

import pygame 
from pygame import *

from pymills.event import filter, listener, Component, \
		PyGameManager

class Test(Component):

	def init(self):
		pygame.init()
		screen = pygame.display.set_mode(
				(640, 480),
				DOUBLEBUF | HWSURFACE)

	@filter()
	def onDEBUG(self, event):
		print event
		return False, event

	@listener("keyup")
	def onKEYUP(self, key, mod):
		if key == K_q:
			raise SystemExit, 0

	@listener("quit")
	def onQUIT(self):
		raise SystemExit, 0
	
def main():

	event = PyGameManager()
	test = Test(event)

	while True:
		try:
			event.process()
			event.flush()
		except KeyboardInterrupt:
			break
		except SystemExit:
			break
	for i in xrange(len(event)):
		event.flush()

if __name__ == "__main__":
	main()
