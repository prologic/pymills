#!/usr/bin/env python
# Filename: test.py
# Module:	test
# Date:		18th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Test Suite

Script to run the PyMills Test Suite.
"""

import sys
import doctest
import unittest

def suite():
	from pymills.tests import event, sockets

	suite = unittest.TestSuite()
	suite.addTest(event.suite())
	suite.addTest(sockets.suite())

	return suite

def main():
	doctest.testmod(sys.modules[__name__])
	unittest.main(defaultTest="suite")

if __name__ == "__main__":
	main()
