# Filename: ann.py
# Module:	ann
# Date:		18th March 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Artificial Neural Networking Library

This library contains classes for use with developing
artificial neural networks.

         InputNode   Node     OutputNode    Neuron
Inputs:     0         1           1          many
Outputs:   many      many       many         many

Types of Neurons:
 * Linear
 * Step
 * Error Calc
 * Sigmoid
"""

from threading import Thread

class SynapseError(Exception):
	pass

class LinkError(Exception):
	pass

class Synapse(Thread):

	def __init__(self, source, target, weight=50.0, decay=False):

		Thread.__init__(self)

		if not isinstance(source, Node):
			raise SynapseError("source must be an instance of Node")
		if not isinstance(target, Node):
			raise SynapseError("target must be an instance of Node")

		self._source = source
		self._target = target
		self._weight = weight
		self._decay = decay
	
	def fire(self, value=0.0):
		self._target.fire(value * self._weight)

class Node(Thread):

	def __init__(self, output=0.0):

		Thread.__init__(self)

		self._inputs = []
		self._outputs = []
		self._output = output
	
	def getOutput(self):
		return self._output

	def setOutput(self, output):
		self._output = output

	def link(self, synapse):

		if (synapse._target == self) and (len(self._inputs) == 1):
			raise LinkError("Node can only have maximum of 1 inputs")

		if synapse._source == self:
			self._outputs.append(synapse)
		if synapse._target == self:
			self._inputs.append(synapse)

	def fire(self, value=0.0):
		self.setOutput(value)
		for output in self._outputs:
			output.fire(self._output)
	
class InputNode(Node):

	def link(self, synapse):

		if (synapse._target == self):
			raise LinkError("InputNode cannot have any inputs")

		if synapse._source == self:
			self._outputs.append(synapse)

	def fire(self, value=0.0):
		Node.fire(self, value)

	def run(self):
		self.fire(self.getOutput())

class OutputNode(Node):

	def __init__(self, output=0.0, func=None, *args):
		Node.__init__(self, output)
		self._func = func
		self._args = args

	def fire(self, value=0.0):
		if callable(self._func):
			self._func(value, self._args)
		Node.fire(self, value)
	
class Neuron(Node):

	def __init__(self, _threshold):
		Node.__init__(self)
		self.__threshold = _threshold
	
	def getThreshold(self):
		return self._threshold

	def setThreshold(self, threshold):
		self._threshold = threshold

	def fire(self, value=0.0):
		self.setOutput(self.getOutput() + value)
		if self.getOutput() > self.__threshold:
			for output in self._outputs:
				output.fire(self._output)
