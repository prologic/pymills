# Module:	email
# Date:		5th December 2007
# Author:	James Mills, prologic at shortcircuit dot net au

"""Email Utilities

A feature-rich Email class allowing you to create and send
multi-part emails as well as a simple sendEmail function
for simpler plain text emails.
"""

import base64
import smtplib
import MimeWriter
from StringIO import StringIO

class Email(object):

	def __init__(self, sender, recipient, subject=""):
		self.message = StringIO()
		self.writer = MimeWriter.MimeWriter(self.message)
		self.writer.addheader('Subject', subject)
		self.writer.startmultipartbody('mixed')

	def add(self, type="text/plain", name=None, fd=None, content=""):
		part = self.writer.nextpart()
		body = part.startbody(type, name)
		if fd is not None:
			body.write(base64.encode(fd))
		else:
			body.write(content)

	def send(self):
		self.writer.lastpart()
		smtp = smtplib.SMTP("localhost")
		smtp.sendmail(
			self.sender,
			self.recipient,
			self.message.getvalue())
		smtp.quit()

def sendEmail(sender, recipient, subject, message):
	"""sendEmail(sender, recipient, subject, message) -> None

	Send a simple email to the given recipient with the
	given subject and message.
	"""

	email = Email(sender, recipient, subject)
	email.add("text/plain", message)
	email.send()
