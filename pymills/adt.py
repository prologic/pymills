# Filename: adt.py
# Module:   adt
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate$
# $Author$
# $Id$

"""Abstract Data Types module."""

class Stack:

	def __init__(self):
		self._stack = []
	
	def __getitem__(self, n):
		if (not self.empty()) and (0 <= (n + 1) <= len(self._stack)):
			return self._stack[(len(self._stack) - (n + 1))]
		else:
			raise StopIteration

	def push(self, item):
		self._stack.append(item)
	
	def pop(self):
		if not self.empty():
			return self._stack.pop()
		else:
			return None
	
	def peek(self, n=0):
		if (not self.empty()) and (0 <= (n + 1) <= len(self._stack)):
			return self._stack[(len(self._stack) - (n + 1))]
		else:
			return None
	
	def empty(self):
		return self._stack == []

class Queue:

	def __init__(self):
		self._queue = []

	def __getitem__(self, n):
		if (not self.empty()) and (0 <= (n + 1) <= len(self._queue)):
			return self._queue[(len(self._queue) - (n + 1))]
		else:
			raise StopIteration
	
	def push(self, item):
		self._queue.insert(0, item)
	
	def pop(self):
		if not self.empty():
			return self._queue.pop()
		else:
			return None
	
	def peek(self, n = 0):
		if (not self.empty()) and (0 <= (n + 1) <= len(self._queue)):
			return self._queue[(len(self._queue) - (n + 1))]
		else:
			return None
	
	def empty(self):
		return self._queue == []
