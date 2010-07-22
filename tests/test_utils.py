# Module:	utils
# Date:		14th January 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Utils Test Suite

Test all functionality of the Utils library.
"""

import unittest

from pymills.utils import notags, getProgName 

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

		self.assertEquals(getProgName(), "nosetests")

def suite():
	return unittest.makeSuite(UtilsTestCase, "test")

if __name__ == "__main__":
	unittest.main()
