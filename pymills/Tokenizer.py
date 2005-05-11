#!/usr/bin/env python

# Filename: Tokenizer.py
# Module:   Tokenizer
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-05-10 00:00:12 +1000 (Tue, 10 May 2005) $
# $Author: prologic $
# $Id: Tokenizer.py 1916 2005-05-09 14:00:12Z prologic $

"""Tokenizer

Tokenizer Class to split strings up into tokens
"""

import string

__version__ = "0.1"
__copyright__ = "CopyRight (C) 2005 by James Mills"
__author__ = "James Mills <prologic@shortcircuit.net.au>"
__url__ = "http://shortcircuit.net.au/~prologic/"

class Tokenizer:
	"""Tokenizer Class

	Class to split a string into tokens with many different
	supporting methods such as: index, last, peek, more, next
	and more...
	"""

	def __init__(self, str, delim = ' '):
		"Initialize class"

		self.str = str
		self.delim = delim

		self.tokens = string.split(self.str, self.delim)
	
	def __getitem__(self, y):
		return self.tokens[y]
	
	def last(self):
		"Return the last token"

		if not self.tokens == []:
			return self.tokens.pop()
		else:
			return ""
	
	def index(self, token):
		"Return position of token"

		if not self.tokens == []:
			return self.tokens.index(token)
		else:
			return -1
	
	def copy(self, s = None, e = None):
		"Return string containing tokens from s to e"

		if not self.tokens == []:
			if s == None:
				s = 0
			if e == None:
				e = len(self.tokens)
			return string.join(self.tokens[s:e], self.delim)
		else:
			return ""
	
	def has(self, token):
		"Return True if token exists"

		return token in self.tokens
	
	def peek(self):
		"Returns the next token but doesn't delete it"

		if not self.tokens == []:
			return self.tokens[0]
		else:
			return ""
	
	def next(self):
		"Return the next token"

		if not self.tokens == []:
			return self.tokens.pop(0)
		else:
			return ""
	
	def delete(self, n = 1):
		"Delete the first n tokens"

		if not self.tokens == []:
			for i in range(n):
				self.tokens.pop(0)
	
	def count(self):
		"Return the number of tokens"

		return len(self.tokens)
	
	def more(self):
		"Return true if more tokens, false otherwise"

		return not self.tokens == []
	
	def rest(self):
		"Return the rest of the tokens"

		return string.join(self.tokens, self.delim)
	
def test():
	"""Test function to perform a self-test on this module.

	To run, type: python Tokenizer.py
	"""

	s = "This is a string with tokens in it."

	tokens = Tokenizer(s)

	while tokens.more():
		print "Token: %s" % tokens.next()

	print s

	print "Tokens 1 to 4: %s" % tokens.copy(1, 4)
	print "No. of tokens: %d" % tokens.count()

	print "Deleting token at pos #1"
	tokens.delete(1)

	print "Has token \"string\" ? %s" % str(tokens.has("string"))
	print "Index of token \"string\" ? %s" % str(tokens.index("string"))
	print "Last token: %s" % tokens.last()
	print "Peek at token: %s" % tokens.peek()
	print "Next token: %s" % tokens.next()
	print "Rest of tokens: %s" % tokens.rest()

	while tokens.more():
		print "Token: %s" % tokens.next()

if __name__ == "__main__":
	test()

#" vim: tabstop=3 nocindent autoindent
