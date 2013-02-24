# Module:   emailtools
# Date:     5th December 2007
# Author:   James Mills, prologic at shortcircuit dot net au

"""Email Tools

A feature-rich Email class allowing you to create and send
multi-part emails as well as a simple sendEmail function
for simpler plain text emails.
"""

import os
import smtplib
import mimetypes
from smtplib import SMTP
from email import encoders
from itertools import chain
from errno import ECONNREFUSED
from mimetypes import guess_type
from subprocess import Popen, PIPE
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from socket import error as SocketError
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from os.path import abspath, basename, expanduser

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


def get_mimetype(filename):
    content_type, encoding = guess_type(filename)
    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"
    return content_type.split("/", 1)


def mimify_file(filename):
    filename = abspath(expanduser(filename))
    basefilename = basename(filename)

    msg = MIMEBase(*get_mimetype(filename))
    msg.set_payload(open(filename, "rb").read())
    msg.add_header("Content-Disposition", "attachment", filename=basefilename)

    encode_base64(msg)

    return msg


def send_email(to, subject, text, **params):
    # Default Parameters
    cc = params.get("cc", [])
    bcc = params.get("bcc", [])
    files = params.get("files", [])
    sender = params.get("sender", "root@localhost")

    recipients = list(chain(to, cc, bcc))

    # Prepare Message
    msg = MIMEMultipart()
    msg.preamble = subject
    msg.add_header("From", sender)
    msg.add_header("Subject", subject)
    msg.add_header("To", ", ".join(to))
    cc and msg.add_header("Cc", ", ".join(cc))

    # Attach the main text
    msg.attach(MIMEText(text))

    # Attach any files
    [msg.attach(mimify_file(filename)) for filename in files]

    # Contact local SMTP server and send Message
    try:
        smtp = SMTP()
        smtp.connect()
        smtp.sendmail(sender, recipients, msg.as_string())
        smtp.quit()
    except SocketError as e:
        if e.args[0] == ECONNREFUSED:
            p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
            p.communicate(msg.as_string())
        else:
            raise
