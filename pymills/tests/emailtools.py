# Module:	utils
# Date:		5th March 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Email Tools Test Suite

Test all functionality of the Email Tools library.
"""

import unittest

from pymills.emailtools import Email

class EmailToolsTestCase(unittest.TestCase):

	def test_Email(self):
		"""Test Email class

		Test the Email class
		"""

		fd = open("/tmp/foo", "w")
		fd.write("This is a test file.")
		fd.close()

		sender = "root@localhost"
		recipient = "root@localhost"
		subject = "Test"
		body = "This is a test email."
		file = "/tmp/foo"
		filename = "foo.txt"

		email = Email(sender, recipient, subject)
		email.add(body)
		email.add(file=file, attach=True, filename=filename)
		email.send()

def suite():
	return unittest.makeSuite(EmailToolsTestCase, "test")