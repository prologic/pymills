# Filename: config.py
# Module:	config
# Date:		18th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Config Test Suite

...
"""

import os
import time
import tempfile
import unittest

from pymills.config import Configuration

class ConfigurationTestCase(unittest.TestCase):

	def setUp(self):
		self.filename = os.path.join(tempfile.gettempdir(), "pymills-test.ini")
		configfile = open(self.filename, "w")
		configfile.close()

	def tearDown(self):
		os.remove(self.filename)

	def test_default(self):
		config = Configuration(self.filename)
		self.assertEquals("", config.get("a", "option"))
		self.assertEquals("value", config.get("a", "option", "value"))

		config.setdefault("a", "option", "value")
		self.assertEquals("value", config.get("a", "option"))

	def test_default_bool(self):
		config = Configuration(self.filename)
		self.assertEquals(False, config.getbool("a", "option"))
		self.assertEquals(True, config.getbool("a", "option", "yes"))
		self.assertEquals(True, config.getbool("a", "option", 1))

		config.setdefault("a", "option", "true")
		self.assertEquals(True, config.getbool("a", "option"))

	def test_read_and_get(self):
		configfile = open(self.filename, "w")
		configfile.writelines(["[a]\n", "option = x\n", "\n"])
		configfile.close()

		config = Configuration(self.filename)
		self.assertEquals("x", config.get("a", "option"))
		self.assertEquals("x", config.get("a", "option", "y"))

	def test_set_and_save(self):
		configfile = open(self.filename, "w")
		configfile.close()

		config = Configuration(self.filename)
		config.set("a", "option", "x")
		self.assertEquals("x", config.get("a", "option"))
		config.save()

		configfile = open(self.filename, "r")
		self.assertEquals(["[a]\n", "option = x\n", "\n"],
						  configfile.readlines())
		configfile.close()

	def test_sections(self):
		configfile = open(self.filename, "w")
		configfile.writelines(["[a]\n", "option = x\n",
							   "[b]\n", "option = y\n"])
		configfile.close()

		config = Configuration(self.filename)
		self.assertEquals(["a", "b"], config.sections())

	def test_options(self):
		configfile = open(self.filename, "w")
		configfile.writelines(["[a]\n", "option = x\n",
							   "[b]\n", "option = y\n"])
		configfile.close()

		config = Configuration(self.filename)
		self.assertEquals(("option", "x"), iter(config.options("a")).next())
		self.assertEquals(("option", "y"), iter(config.options("b")).next())
		self.assertRaises(StopIteration, iter(config.options("c")).next)

def suite():
	return unittest.makeSuite(ConfigurationTestCase, "test")

if __name__ == "__main__":
	unittest.main()
