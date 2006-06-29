# Filename: __init__.py
# Module:	__init__
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Teste Suite

Test Suite for PyMills. This will test every module
in PyMills. As much as possible, all functionality
is tested in each module.
"""
import unittest

from pymills.tests import event
from pymills.tests import config
from pymills.tests import sockets

def suite():
	suite = unittest.TestSuite()
	suite.addTest(event.suite())
	suite.addTest(config.suite())
	suite.addTest(sockets.suite())
	return suite

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
