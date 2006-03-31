# Filename: logic.py
# Module:	logic
# Date:		21st March 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: logic.py 97 2005-11-28 06:41:28Z prologic $

"""Logic Module

This module contains some logic functions. At the moment,
these are merely short-cuts of code.
"""

def andAll(l, c):
	"""Compare all values in l against c in an AND operation

	l - list of values
	c - value to compare against

	This function will result in either True or False, by
	comparing each of the elements in l against c.
	"""

	return reduce(
			lambda x, y: x and y, map(lambda x: x is c, l))

def runTests():
	pass

if __name__ == "__main__":
	runTests()
