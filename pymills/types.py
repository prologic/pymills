# Filename: datatypes.py
# Module:	datatypes
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Data Types Library

...
"""

class OrderedDict(dict):

	def __init__(self, d={}):
		self._keys = d.keys()
		dict.__init__(self, d)

	def __delitem__(self, key):
		dict.__delitem__(self, key)
		self._keys.remove(key)

	def __setitem__(self, key, item):
		dict.__setitem__(self, key, item)
		if key not in self._keys:
			self._keys.append(key)

	def clear(self):
		dict.clear(self)
		self._keys = []

	def items(self):
		for i in self._keys:
			yield i, self[i]

	def keys(self):
		return self._keys

	def popitem(self):
		if len(self._keys) == 0:
			raise KeyError("popitem(): dictionary is empty")
		else:
			key = self._keys[-1]
			val = self[key]
			del self[key]
			return key, val

	def setdefault(self, key, failobj=None):
		dict.setdefault(self, key, failobj)
		if key not in self._keys:
			self._keys.append(key)

	def update(self, d):
		for key in d.keys():
			if not self.has_key(key):
				self._keys.append(key)
		dict.update(self, d)

	def iteritems(self):
		for key in self._keys:
			yield key, self[key]

	def itervalues(self):
		for key in self._keys:
			yield self[key]

	def values(self):
		return [self[k] for k in self._keys]

	def iterkeys(self):
		for key in self._keys:
			yield key

	def index(self, key):
		if not self.has_key(key):
			raise KeyError(key)
		return self._keys.index(key)

class Stack(object):

	def __init__(self, size=None):
		super(Stack, self).__init__()

		self._stack = []
		self._size = size

	def __len__(self):
		return len(self._stack)

	def __getitem__(self, n):
		if (not self.empty()) and (0 <= (n + 1) <= len(self._stack)):
			return self._stack[(len(self._stack) - (n + 1))]
		else:
			raise StopIteration

	def push(self, item):
		self._stack.append(item)
		if self._size is not None:
			self._stack = self._stack[self._size:]

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

class Queue(object):

	def __init__(self, size=None):
		super(Queue, self).__init__()

		self._queue = []
		self._size = size

	def __len__(self):
		return len(self._queue)

	def __getitem__(self, n):
		if (not self.empty()) and (0 <= (n + 1) <= len(self._queue)):
			return self._queue[(len(self._queue) - (n + 1))]
		else:
			raise StopIteration

	def push(self, item):
		self._queue.insert(0, item)
		if self._size is not None:
			self._queue = self._queue[:self._size]

	def get(self, n=0, remove=False):
		if (not self.empty()) and (0 <= (n + 1) <= len(self._queue)):
			r = self._queue[(len(self._queue) - (n + 1))]
			if remove:
				del self._queue[(len(self._queue) - (n + 1))]
			return r
		else:
			return None

	def pop(self, n=0):
		return self.get(n, True)

	def peek(self, n=0):
		return self.get(n)

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

	def __delitem__(self, key):
		dict.__delitem__(self, key.lower())

	def __setitem__(self, key, value):
		dict.__setitem__(self, key.lower(), value)

	def __getitem__(self, key):
		return dict.__getitem__(self, key.lower())

	def get(self, key, default=None):
		return dict.get(self, key.lower(), default)

	def has_key(self, key):
		return dict.has_key(self, key.lower())
