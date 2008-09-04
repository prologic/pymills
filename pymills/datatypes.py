# Filename: datatypes.py
# Module:	datatypes
# Date:		04th August 2004
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Data Types Library

Various custom data types not available in the standard
python library.
"""

class OrderedDict(dict):

	def __init__(self, d={}):
		super(OrderedDict, self).__init__(d)
		self._keys = d.keys()

	def __repr__(self):
		return "{%s}" % ", ".join([("%s: %s" % (repr(k), repr(v))) for k, v in self.iteritems()])

	def __delitem__(self, key):
		super(OrderedDict, self).__delitem__(key)
		self._keys.remove(key)

	def __setitem__(self, key, item):
		super(OrderedDict, self).__setitem__(key, item)
		if key not in self.keys():
			self._keys.append(key)

	def clear(self):
		super(OrderedDict, self).clear()
		self._keys = []

	def items(self):
		for key in self.keys():
			value = self[key]
			yield key, value

	def keys(self):
		return self._keys

	def popitem(self):
		if len(self.keys()) == 0:
			raise KeyError("popitem(): dictionary is empty")
		else:
			key = self.keys()[-1]
			value = self[key]
			del self[key]
			return key, value

	def setdefault(self, key, failobj=None):
		super(OrderedDict, self).setdefault(key, failobj)
		if key not in self.keys():
			self._keys.append(key)

	def update(self, d):
		for key in d.keys():
			if not self.has_key(key):
				self._keys.append(key)
		super(OrderedDict, self).update(d)

	def iteritems(self):
		for key in self.keys():
			value = self[key]
			yield key, value

	def itervalues(self):
		for key in self.keys():
			yield self[key]

	def values(self):
		return [self[key] for key in self.keys()]

	def iterkeys(self):
		for key in self.keys():
			yield key

	def index(self, key):
		if not self.has_key(key):
			raise KeyError(key)
		return self.keys().index(key)

class Stack(object):

	def __init__(self, size=None):
		super(Stack, self).__init__()

		self._stack = []
		self._size = -size

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

	def top(self):
		return self.peek()

	def bottom(self):
		return self.peek(len(self) - 1)

	def empty(self):
		return self._queue == []

	def size(self):
		return self._size

	def full(self):
		return len(self) == self.size()

class CaselessList(list):

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

class Null(object):

	def __getattr__(self, mname):
		return self

	def __setattr__(self, name, value):
		return self

	def __delattr__(self, name):
		return self

	def __repr__(self):
		return "<Null>"

	def __str__(self):
		return ""
	
	def __int__(self):
		return 0
	
	def __float__(self):
		return 0.0
	
	def __long__(self):
		return 0.0
	
	def __radd__(self, y):
		return y

	def __rsub__(self, y):
		return y

	def __rmul__(self, y):
		return y

	def __rdiv__(self, y):
		return y
	
	def __eq__(self, y):
		return isinstance(y, self.__class__)
	
	def __len__(self):
		return 0

	def __add__(self, y):
		return y

	def __sub__(self, y):
		return y

	def __mul__(self, y):
		return y

	def __div__(self, y):
		return y
