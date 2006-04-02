# Filename: event.py
# Module:	event
# Date:		2nd April 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Event Library

....
"""
class Event:

	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

class EventManager:

	def __init__(self):
		self._listeners = {}

	def addListener(self, listener, *channels):

		listeners = self._listeners

		for channel in channels:
			if not listeners.has_key(channel):
				listeners[channel] = []
			listeners[channel].append(listener)
	
	def removeListener(self, listener, *channels):

		listeners = self._listeners

		if len(channels) == 0:
			keys = listeners.keys()
		else:
			keys = channels

		for channel in keys:
			listeners[channel].remove(listener)
	
	def sendEvent(self, event, channel, source=None):

		event.source = source

		listeners = self._listeners.get(channel, [])
		for listener in listeners:
			listener(event)
