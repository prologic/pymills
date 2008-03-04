# Module:	utils
# Date:		14th January 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Utils Test Suite

Test all functionality of the Utils library.
"""

import unittest

from pymills.utils import notags, getProgName, caller

class UtilsTestCase(unittest.TestCase):

	def test_notags(self):
		"""Test notags functions

		Test the "notags" function.
		"""

		x = "<html>foo</html>"
		y = "foo"
		self.assertEquals(notags(x), y)

	def test_getProgName(self):
		"""Test getProgName functions

		Test the "getProgName" function.
		"""

		self.assertEquals(getProgName(), "run.py")

	def test_caller(self):
		"""Test caller functions

		Test the "caller" function.
		"""

		self.assertEquals(caller(1), "run")
		self.assertEquals(caller(), "run")
		self.assertEquals(caller(0), "test_caller")
		self.assertEquals(caller(-1), "caller")

def suite():
	return unittest.makeSuite(UtilsTestCase, "test")
