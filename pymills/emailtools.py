# Module:	emailtools
# Date:		5th December 2007
# Author:	James Mills, prologic at shortcircuit dot net au

"""Email Tools

A feature-rich Email class allowing you to create and send
multi-part emails as well as a simple sendEmail function
for simpler plain text emails.
"""

import os
import smtplib
import mimetypes
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

COMMASPACE = ", "

class Email(object):

	def __init__(self, sender, recipients, subject="", cc=[], bcc=[]):
		self.sender = sender

		if type(recipients) is str:
			self.recipients = [recipients]
		else:
			self.recipients = recipients
		self.subject = subject

		if type(cc) is str:
			self.cc = [cc]
		else:
			self.cc = cc

		if type(bcc) is str:
			self.bcc = [bcc]
		else:
			self.bcc = bcc

		self.msg = MIMEMultipart()
		self.msg["From"] = sender
		self.msg["Subject"] = subject
		self.msg["To"] = COMMASPACE.join(self.recipients)
		self.msg.preamble = subject

	def _getType(self, file):
		ctype, encoding = mimetypes.guess_type(file)
		if ctype is None or encoding is not None:
			ctype = 'application/octet-stream'
		return ctype.split('/', 1)

	def add(self, text="", file=None, attach=False, filename=None):
		if file is not None:
			mainType, subType = self._getType(file)

			if attach:
				fp = open(file, 'rb')
				msg = MIMEBase(mainType, subType)
				msg.set_payload(fp.read())
				fp.close()
				encoders.encode_base64(msg)
				if filename is not None:
					filename_tmp = filename
				else:
					filename_tmp = os.path.basename(file)
				msg.add_header(
					'Content-Disposition',
					'attachment',
					filename=filename_tmp)
			else:
				if mainType == 'text':
					fp = open(file, "r")
					msg = MIMEText(fp.read(), _subtype=subType)
					fp.close()
				elif mainType == 'image':
					fp = open(file, 'rb')
					msg = MIMEImage(fp.read(), _subtype=subType)
					fp.close()
				elif mainType == 'audio':
					fp = open(file, 'rb')
					msg = MIMEAudio(fp.read(), _subtype=subType)
					fp.close()
				else:
					fp = open(file, 'rb')
					msg = MIMEBase(mainType, subType)
					msg.set_payload(fp.read())
					fp.close()
					encoders.encode_base64(msg)
					if filename is not None:
						filename_tmp = filename
					else:
						filename_tmp = os.path.basename(file)
					msg.add_header(
						'Content-Disposition',
						'attachment',
						filename=filename_tmp)
		else:
			msg = MIMEText(text)

		self.msg.attach(msg)

	def send(self):

		recipients = self.recipients
		
		if self.cc:
			self.msg["Cc"] = COMMASPACE.join(self.cc)
			recipients += self.cc
		if self.bcc:
			recipients += self.bcc

		s = smtplib.SMTP()
		s.connect()
		s.sendmail(
			self.sender,
			self.recipients,
			self.msg.as_string())
		s.close()

def sendEmail(sender, recipient, subject, message):
	"""sendEmail(sender, recipient, subject, message) -> None

	Send a simple email to the given recipient with the
	given subject and message.
	"""

	email = Email(sender, recipient, subject)
	email.add(message)
	email.send()
