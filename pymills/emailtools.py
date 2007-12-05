# Module:	emailtools
# Date:		5th December 2007
# Author:	James Mills, prologic at shortcircuit dot net au

"""Email Tools

A feature-rich Email class allowing you to create and send
multi-part emails as well as a simple sendEmail function
for simpler plain text emails.
"""

import smtplib
import mimetypes
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

class Email(object):

	def __init__(self, sender, recipient, subject=""):
		self.sender = sender
		self.recipient = recipient
		self.subject = subject

		self.msg = MIMEMultipart()
		self.msg["From"] = sender
		self.msg["Subject"] = subject
		self.msg["To"] = recipient
		self.msg.preamble = subject

	def _getType(self, file):
		ctype, encoding = mimetypes.guess_type(file)
		if ctype is None or encoding is not None:
			ctype = 'application/octet-stream'
		return ctype.split('/', 1)

	def add(self, text="", file=None):
		if file is not None:
			mainType, subType = self._getType(file)
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
			self.msg.add_header(
				'Content-Disposition',
				'attachment',
				filename=os.path.basename(file))
		else:
			msg = MIMEText(text)

		self.msg.attach(msg)

	def send(self):
		s = smtplib.SMTP()
		s.connect()
		s.sendmail(
			self.sender,
			self.recipient,
			self.msg.as_string())
		s.close()

def sendEmail(sender, recipient, subject, message):
	"""sendEmail(sender, recipient, subject, message) -> None

	Send a simple email to the given recipient with the
	given subject and message.
	"""

	email = Email(sender, recipient, subject)
	email.add("text/plain", message)
	email.send()
