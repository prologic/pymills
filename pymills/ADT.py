#!/usr/bin/env python

# Filename: ADT.py
# Module:   ADT
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-08 21:16:31 +1000 (Fri, 08 Apr 2005) $
# $Author: prologic $
# $Id: ADT.py 1572 2005-04-08 11:16:31Z prologic $

"""Abstract Data Types module.

This library contains Abstract Data Types.
"""

__version__ = "0.2"
__copyright__ = "CopyRight (C) 2005 by James Mills"
__author__ = "James Mills <prologic@shortcircuit.net.au>"
__url__ = "http://shortcircuit.net.au/~prologic/"

class Stack:
	"""Stack Class - FILO (First In Last Out)

	This class is simply an extenstion or encapsulation of a list.
	"""

	def __init__(self):
		"Initialize the internal stack"

		self._stack = []
	
	def push(self, n):
		"Push item n onto the stack."

		self._stack.append(n)
	
	def pop(self):
		"Pop off and return the first item on the stack."

		if not self.empty():
			return self._stack.pop()
		else:
			return None
	
	def peek(self, n = 0):
		"Peek, but don't remove the first nth item on the stack."

		if (not self.empty()) and ((n + 1) <= len(self._stack)):
			return self._stack[(len(self._stack) - (1 + n))]
		else:
			return None
	
	def empty(self):
		"Return True if the stack is empty."

		return self._stack == []

class Queue:
	"""Queue Class - FIFO (First In First Out)

	This class is simply an extenstion or encapsulation of a list.
	"""

	def __init__(self):
		"Initialize the internal queue"

		self._queue = []
	
	def push(self, n):
		"Push item n onto the queue."

		self._queue.insert(0, n)
	
	def pop(self):
		"Pop off and return the first item in the queue."

		if not self.empty():
			return self._queue.pop()
		else:
			return None
	
	def peek(self, n = 0):
		"Peek, but don't remove the first nth item in the queue."

		if (not self.empty()) and ((n + 1) <= len(self._queue)):
			return self._queue[(len(self._queue) - (1 + n))]
		else:
			return None
	
	def empty(self):
		"Return True if the queue is empty."

		return self._queue == []
	
def test():
	"""Test function to perform a self-test on this module.

	To run, type: python ADT.py
	"""

	stack = Stack()

	stack.push("A")
	stack.push("B")
	stack.push("C")

	while not stack.empty():
		print stack.pop()
	
	queue = Queue()

	for x in range(1, 10):
		queue.push(x)
	
	while not queue.empty():
		print queue.pop()

if __name__ == '__main__':
	test()

#" vim: tabstop=3 nocindent autoindent
