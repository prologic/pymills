# Filename: rit.py
# Module:	rit
# Date:		22nd March 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Relational Information Trees

A reational information tree consists of a list of nodes.
A node can have many sub-nodes.
Nodes have properties and
Nodes can have relationships with other nodes.
"""

class Node:

	def __init__(self, name):
		self._name = name

		self._nodes = []

class Root(Node):

	def __init__(self, name="/"):
		Node.__init__(name)
	
	def load(self, file):
		pass
	
	def save(self, file):
		pass

class Property:
	pass

def runTests():
	pass

if __name__ == '__main__':
	runTests()
