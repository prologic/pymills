# Filename: __init__.py
# Module:	__init__
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Teste Suite

...
"""
import unittest

from pymills.tests import event
from pymills.tests import config

def suite():
	suite = unittest.TestSuite()
	suite.addTest(event.suite())
	suite.addTest(config.suite())
	return suite

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
