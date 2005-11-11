# Filename: adt.py
# Module:	adt
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Abstract Data Types

This modules contains some commonoly used ADTs that can be used
in your program. More will be implemented later...
"""

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

class CaselessList(list):

#	def __new__(self):
#		pass

#	def update(self):
#		pass

#	def setdefault(self):
#		pass
	
	def __contains__(self, y):
		return list.__contains__(self, y.lower())

	def __delitem__(self, y):
		list.__delitem__(self, y.lower())
	
	def __setitem__(self, y):
		list.__setitem__(self, y.lower())

	def __getitem__(self, y):
		return list.__getitem__(self, y)

	def append(self, obj):
		if type(obj) is list:
			for y in obj:
				list.append(self, y.lower())
		elif type(obj) is str:
			list.append(self, obj.lower())
		else:
			list.append(self, y)
	
	def remove(self, value):
		if type(value) is str:
			list.remove(self, value.lower())
		else:
			list.remove(self, value)

class CaselessDict(dict):

#	def __new__(self):
#		pass

#	def update(self):
#		pass

#	def setdefault(self):
#		pass
	
	def __contains__(self, value):
		dict.__contains__(self, value.lower())

	def __delitem__(self, key):
		dict.__delitem__(self, key.lower())
	
	def __setitem__(self, key, value):
		dict.__setitem__(self, key.lower(), value)

	def __getitem__(self, key):
		return dict.__getitem__(self, key.lower())

	def get(self, key, default=None):
		return dict.get(self, key.lower())

	def has_key(self, key):
		return dict.has_key(self, key.lower())
