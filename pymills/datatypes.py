
class OrderedDict(dict):

	def __init__(self, d={}):
		self._keys = d.keys()
		dict.__init__(self, d)

	def __delitem__(self, key):
		dict.__delitem__(self, key)
		self._keys.remove(key)

	def __setitem__(self, key, item):
		dict.__setitem__(self, key, item)
		if not hasattr(self, '_keys'):
			self._keys = [key,]
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

	def setdefault(self, key, failobj = None):
		dict.setdefault(self, key, failobj)
		if key not in self._keys:
			self._keys.append(key)

	def update(self, d):
		for key in d.keys():
			if not self.has_key(key):
				self._keys.append(key)
		dict.update(self, d)

	def values(self):
		for i in self._keys:
			yield self[i]

	def index(self, key):
		if not self.has_key(key):
			raise KeyError(key)
		return self._keys.index(key)
