# Module:	db
# Date:		27th December 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""DB Test Suite

Test all functionality of the db library.
"""

import unittest

from pymills.db import newDB

class EventTestCase(unittest.TestCase):

	def testSQLite(self):
		"""Test SQLite Sessions

		Tests the database library using SQLite Sessions.
		"""

		db = newDB("sqlite://:memory:")
		x = db.do("create table names (firstname, lastname)")
		self.assertEquals(x, [])
		x = db.do("insert into names values ('James', 'Mills')")
		self.assertEquals(x, [])
		x = db.do("insert into names values ('Danny', 'Rawlins')")
		self.assertEquals(x, [])
		rows = db.do("select firstname, lastname from names")
		self.assertEquals(rows[0].firstname, "James")
		self.assertEquals(rows[0].lastname, "Mills")

def suite():
	return unittest.makeSuite(EventTestCase, "test")
