# Module:	ann
# Date:		18th March 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Artificial Neural Networking Library

...
"""

import math
from time import time, sleep

from event import listener, Event, UnhandledEvent, Worker, \
		EventManager

class SignalEvent(Event):

	def __init__(self, source, level):
		Event.__init__(self, source=source, level=level)

class Node(Worker):

	def __repr__(self):
		return "<Node running=%s>" % self.isRunning()

	def fire(self, level=1.0):
		self.event.push(SignalEvent(self, level), "signal")
	
	def run(self):
		while self.isRunning():
			try:
				self.flush()
			except UnhandledEvent:
				pass
			sleep(0.01)

def new_node(*args, **kwargs):
	class NewNode(Node):
		pass
	return NewNode(*args, **kwargs)
	
class Synapse(Node):

	def __init__(self, event=None, weight=1.0):
		Node.__init__(self)
		self._weight = weight

	def __repr__(self):
		return "<Synapse weight=%0.2f>" % self._weight

	def _get_weight(self):
		try:
			return self._weight
		except:
			return None

	def _set_weight(self, weight):
		self._weight = weight

	@listener("signal")
	def onSIGNAL(self, source, level):
		self.fire(level * self._weight)
	
	weight = property(_get_weight, _set_weight)

def new_synapse(*args, **kwargs):
	class NewSynapse(Synapse):
		pass
	return NewSynapse(*args, **kwargs)

class _StepNeuron(object):

	def compute(self):
		if self._level > self._threshold:
			self.fire(1.0)
		else:
			self.fire(0.0)

class _SigmoidNeuron(object):

	def compute(self):
		self.fire(math.exp(-1 * self._level))

class Neuron(Node):

	def __init__(self, event=None, threshold=1.0, type="step"):
		Node.__init__(self)

		self._threshold = threshold
		self._level = 0.0
		self._ls = None

		if type == "step":
			base = _StepNeuron
		elif type == "sigmoid":
			base = _SigmoidNeuron
		else:
			raise TypeError("Invalid type")

		self.__class__.__bases__ += (base,)

	def __repr__(self):
		return "<Neuron threshold=%0.2f level=%0.2f>" % (
				self._threshold, self._level)
	
	def _get_threshold(self):
		try:
			return self._threshold
		except:
			return None

	def _set_threshold(self, threshold):
		self._threshold = threshold

	@listener("signal")
	def onSIGNAL(self, source, level):
		self._ls = time()
		self._level += level

	def run(self):
		while self.isRunning():
			if self._ls is not None and (time() - self._ls > 0.01):
				self.compute()
				self._level = 0.0
				self._ls = None
			try:
				self.event.flush()
			except UnhandledEvent:
				pass
			sleep(0.01)
	
	threshold = property(_get_threshold, _set_threshold)

def new_neuron(*args, **kwargs):
	class NewNeuron(Neuron):
		pass
	return NewNeuron(*args, **kwargs)

class Output(Node):

	def do(self):
		pass

	@listener("signal")
	def onSIGNAL(self, source, level):
		self.do()

def new_output(*args, **kwargs):
	class NewOutput(Output):
		pass
	return NewOutput(*args, **kwargs)
