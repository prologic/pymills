# Module:	debugger
# Date:		2nd April 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Debugger

Debugger component used to "debug"/"print" each event in a system.
"""

import sys

from pymills.event import filter
from pymills.event.core import Component


class Debugger(Component):

	IgnoreEvents = []
	IgnoreChannels = []

	enabled = True

	def disable(self):
		self.enabled = False
		self.unregister()

	def enable(self):
		self.enabled = True
		self.register(self.manager)

	def toggle(self):
		if self.enabled:
			self.disable()
		else:
			self.enable()

	def set(self, flag):
		if (not self.enabled) and flag:
			self.enable()
		elif self.enabled and (not flag):
			self.disable()

	@filter()
	def onEVENTS(self, *args, **kwargs):
		channel = event.channel
		if True in [event.name == name for name in self.IgnoreEvents]:
			return
		elif channel in self.IgnoreChannels:
			return
		else:
			print >> sys.stderr, event
