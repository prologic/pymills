# Module:	ann
# Date:		18th March 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Artificial Neural Networking Library

...
"""

from time import sleep

from event import listener, Event, Worker, \
		EventManager

class SignalEvent(Event):

	def __init__(self, source, level):
		Event.__init__(self, source=source, level=level)

class Node(Worker):

	def __repr__(self):
		return "<Node>"

	def fire(self, level=1.0):
		self.send(SignalEvent(self, level), "signal")

def new_node(*args, **kwargs):
	class NewNode(Node):
		pass
	return NewNode(*args, **kwargs)
	
class Synapse(Node):

	def __init__(self, event, weight=0.0):
		Node.__init__(self, event)
		self._weight = weight

	def __repr__(self):
		return "<Synapse weight=%0.2f>" % self._weight

	def _get_weight(self):
		return self._weight

	def _set_weight(self, weight):
		self._weight = weight

	@listener("signal")
	def onSIGNAL(self, source, level):
		self.fire(level * self._weight)
	
#	weight = property(_get_weight, _set_weight)

def new_synapse(*args, **kwargs):
	class NewSynapse(Synapse):
		pass
	return NewSynapse(*args, **kwargs)

class Neuron(Node):

	def __init__(self, event, threshold=1.0):
		Node.__init__(self, event)
		self._threshold = threshold
		self._level = 0.0

	def __repr__(self):
		return "<Neuron threshold=%0.2f level=%0.2f>" % (
				self._threshold, self._level)
	
	def _get_threshold(self):
		return self._threshold

	def _set_threshold(self, threshold):
		self._threshold = threshold

	@listener("signal")
	def onSIGNAL(self, source, level):
		self._level += level
		if self._level > self._threshold:
			self.fire()
			self._level = 0.0

	def run(self):
		while self.isRunning():
			sleep(0.1)
			self._level = 0.0
		print "%s terminating..." % self
	
#	threshold = property(_get_threshold, _set_threshold)

def new_neuron(*args, **kwargs):
	class NewNeuron(Neuron):
		pass
	return NewNeuron(*args, **kwargs)
