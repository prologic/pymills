# Filename: ann.py
# Module:	ann
# Date:		18th March 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Artificial Neural Networking Library

This library contains classes for use with developing
artificial neural networks.
"""

class Neuron:

	def __init__(self):
		self._inputs = []
		self._weights = []
		self._output = 0.0
		self._threshold = 0.0

	def getOutput(self):
		"Return the output of this Neuron"

		return self._output

	def setOutput(self, output):
		"Set the output of this Neuron to output"

		self._output = output
	
	def setThreshold(self, threshold):
		"Set the threshhold"

		self._threshold = threshold

	def link(self, neuron, weight):
		"""Adds a link to another neuron with the given weight

		neuron - Neuron object
		weight - weighting of synapse (link)
		"""

		self._inputs.append(neuron)
		self._weights.append(weight)

	def calc(self):
		if self._inputs == []:
			return self._output

		sum = 0.0
		for i in range(0, len(self._inputs)):
			sum += self._inputs[i].getOutput() * self._weights[i]

		self._output = self.squash(sum)
		return self._output

	def squash(self, x):
		if x > self._threshold:
			y = 1.0 
		else:
			y = 0.0
		return y

##
## Tests
##

def test():
	pass

if __name__ == "__main__":
	test()
