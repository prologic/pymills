#!/usr/bin/env python
# Filename: test.py
# Module:	test
# Date:		18th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Test Suite

Script to run the PyMills Test Suite.
"""

import sys
import unittest

def suite():
	from tests import db, event, sockets
	from tests import utils, emailtools

	suite = unittest.TestSuite()
	suite.addTest(db.suite())
	suite.addTest(event.suite())
	suite.addTest(sockets.suite())
	suite.addTest(utils.suite())
	suite.addTest(emailtools.suite())

	return suite

def main():
	unittest.main(defaultTest="suite")

if __name__ == "__main__":
	main()
