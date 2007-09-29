#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import pygame
from pygame import *

from pymills.event import filter, listener, Component, \
		PyGameManager

class Test(Component):

	def __init__(self, event):
		Component.__init__(self, event)

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

	from time import sleep
	sleep(1)

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
