#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep

import pygame
from pygame import *

from pymills.event import *

class Pygame(Component):

	def __init__(self, *args, **kwargs):
		super(Pygame, self).__init__(*args, **kwargs)

		pygame.init()
		screen = pygame.display.set_mode((640, 480),	DOUBLEBUF | HWSURFACE)

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
