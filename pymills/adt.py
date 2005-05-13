# Filename: adt.py
# Module:   adt
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-04-08 21:16:31 +1000 (Fri, 08 Apr 2005) $
# $Author: prologic $
# $Id: adt.py 1572 2005-04-08 11:16:31Z prologic $

"""Abstract Data Types module."""

class Stack(list):
	"""Stack - FILO (First In Last Out)

	This class implements a standard FILO stack with all of the
	operations of the standard stack: push, pop, peek, etc.

	Example:
	"""

	def __init__(self, sequence=[]):
		"""Initialize the stack

		This will initialize and create the Stack Object.
		If given an initial sequence, that sequence is used as
		part of the new Stack.

		Args:
		   sequence : list
		   "An initial Stack"
		"""

		list.__init__(self, sequence)
	
	def push(self, item):
		"""Push item onto the stack.
		
		Args:
		   item : object -> True
		"""

		self.append(item)
	
	def pop(self):
		"""Pop off and return the first item on the stack.

		Returns:
		   item or None
		"""

		if not self.empty():
			return self.__stack.pop()
		else:
			return None
	
	def peek(self, n = 0):
		"""Peek at the first item on the stack and return it
		
		Provied that the stack is NOT empty, the first item on
		the stack will be returned, but unlike pop() it will NOT
		be removed. If the stack is empty, then None is returned.

		Args:
		   n : int -> 0 <= (n + 1) < N
		      (where N is the number of items in the stack)

		Returns:
		   item or None
		"""

		if (not self.empty()) and (0 <= (n + 1) < len(self.__stack)):
			return self.__stack[(len(self.__stack) - (n + 1))]
		else:
			return None
	
	def empty(self):
		"""Return True if the stack is empty.
		
		Args:
		   None
		
		Returns:
		   True or False
		"""

		return self.__stack == []

class Queue:
	"""Queue Class - FIFO (First In First Out)

	This class is simply an extenstion or encapsulation of a list.
	It provides the basic functionality of a standard Queue.

	Example:
	>>> import adt
	>>> queue = adt.Queue()
	>>> queue.push("foo")
	>>> queue.push("bar")
	>>> queue.peek()
	'foo'
	>>> queue.pop()
	'foo'
	>>> queue.empty()
	False
	>>> queue.pop()
	'bar'
	>>> queue.empty()
	True
	"""

	def __init__(self):
		"""Initialize the queue"""

		self.__queue = []
	
	def push(self, item):
		"""Push item onto the queue.
		
		Args:
		   item : a value of any type

		Returns:
		   None
		"""

		self.__queue.insert(0, item)
	
	def pop(self):
		"""Pop off and return the first item on the queue.

		Provided the queue is NOT empty, the first item on
		the queue will be removed and returned otherwise
		None is returned.

		Args:
		   None

		Returns:
		   item or None
		"""

		if not self.empty():
			return self.__queue.pop()
		else:
			return None
	
	def peek(self, n = 0):
		"""Peek at the first item on the queue and return it
		
		Provied that the queue is NOT empty, the first item on
		the queue will be returned, but unlike pop() it will NOT
		be removed. If the queue is empty, then None is returned.

		Args:
		   n : int -> 0 <= (n + 1) < N
		      (where N is the number of items in the queue)

		Returns:
		   item or None
		"""

		if (not self.empty()) and (0 <= (n + 1) < len(self.__queue)):
			return self.__queue[(len(self.__queue) - (n + 1))]
		else:
			return None
	
	def empty(self):
		"""Return True if the queue is empty.
		
		Args:
		   None
		
		Returns:
		   True or False
		"""

		return self.__queue == []
