#!/usr/bin/env python
# Filename: test.py
# Module:	test
# Date:		18th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Test Suite

Script to run the PyMills Test Suite.
"""

import unittest

def suite():
	import pymills.tests

	suite = unittest.TestSuite()
	suite.addTest(pymills.tests.suite())

	return suite

if __name__ == "__main__":
	import doctest, sys
	doctest.testmod(sys.modules[__name__])
	unittest.main(defaultTest="suite")
