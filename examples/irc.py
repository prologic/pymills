#!/usr/bin/env python

import re
import os
import sys
import urwid
import curses
import socket
from time import sleep
from select import select
from inspect import getargspec
from traceback import format_exc
from urwid.raw_display import Screen

from pymills.misc import backMerge
from pymills.sockets import TCPClient
from pymills.irc import sourceSplit, IRC, ERR_NICKNAMEINUSE
from pymills.event import filter, listener, Component, \
		EventManager

MAIN_TITLE = "PyMills IRC Client"

HELP_STRINGS = {
"main": "For help, type: /help"
}

class Client(TCPClient, IRC):

	def __init__(self, event):
		TCPClient.__init__(self, event)
		IRC.__init__(self)

	def ircRAW(self, data):
		self.write(data + "\r\n")
	
	@listener("read")
	def onREAD(self, line):
		TCPClient.onREAD(self, line)
		IRC.onREAD(self, line)
	
class MainWindow(Screen, Component):

	def __init__(self, event, client):
		Screen.__init__(self)
		Component.__init__(self, event)

		self.client = client
		self.channel = None

		self.client.setNick(
				os.getenv("USER", "PyMills"))
		self.client.setIdent(
				os.getenv("USER", "PyMills"))

		self.cmdRegex = re.compile(
				"\/(?P<command>[a-z]+) ?"
				"(?P<args>.*)(?iu)")

		self.register_palette([
				("title", "white", "dark blue", "standout"),
				("line", "light gray", "black"),
				("help", "white", "dark blue")])

#		self.lines = []
		self.body = urwid.ListBox([])
		self.lines = self.body.body
		self.body.set_focus(len(self.lines))

		self.title = urwid.Text(MAIN_TITLE)
		self.header = urwid.AttrWrap(self.title, "title")

		self.help = urwid.AttrWrap(
				urwid.Text(
					HELP_STRINGS["main"]), "help")
		self.input = urwid.Edit(caption="%s> " % self.channel)
		self.footer = urwid.Pile([self.help, self.input])

		self.top = urwid.Frame(self.body, self.header,
				self.footer)
	
	def process(self):
		size = self.get_cols_rows()

		if not select(
				self.get_input_descriptors(),
				[], [], 0.1)[0] == []:

			timeout, keys, raw = self.get_input_nonblocking()

			for k in keys:
	
				if k == "window resize":
					size = self.get_cols_rows()
					continue
				elif k == "enter":
					self.processCommand(self.input.get_edit_text())
					self.input.set_edit_text("")
					continue

				self.top.keypress(size, k)
				self.input.set_edit_text(
						self.input.get_edit_text() + k)

		self.update_screen(size)

	def unknownCommand(self, command):
		self.lines.append(
				urwid.Text(
					"Unknown command: %s" % command))
	
	def syntaxError(self, command, args, expected):
		self.lines.append(
				urwid.Text(
					"Syntax error (%s): %s Expected: %s" % (
						command, args, expected)))

	def processCommand(self, s):

		match = self.cmdRegex.match(s)
		if match is not None:

			command = match.groupdict()["command"]
			if not match.groupdict()["args"] == "":
				tokens = match.groupdict()["args"].split(" ")
			else:
				tokens = []

			fn = "cmd" + command.upper()
			if hasattr(self, fn):
				f = getattr(self, fn)
				if callable(f):

					args, vargs, kwargs, default = getargspec(f)
					args.remove("self")
					if len(args) == len(tokens):
						if len(args) == 0:
							f()
						else:
							f(*tokens)
					else:
						if len(tokens) > len(args):
							if vargs is None:
								if len(args) > 0:
									factor = len(tokens) - len(args) + 1
									f(*backMerge(tokens, factor))
								else:
									print "1"
									self.syntaxError(command,
											" ".join(tokens),
											" ".join(
												[x for x in args + [vargs]
													if x is not None]))
							else:
								f(*tokens)
						elif default is not None and \
								len(args) == (
										len(tokens) + len(default)):
							f(*(tokens + list(default)))
						else:
							self.syntaxError(command,
									" ".join(tokens),
									" ".join(
										[x for x in args + [vargs]
											if x is not None]))
		else:
			if self.channel is not None:
				self.lines.append(urwid.Text(
					"<%s> %s" % (self.client.getNick(), s)))
				self.client.ircPRIVMSG(self.channel, s)
			else:
				self.lines.append(urwid.Text(
					"No channel joined. Try /join #<channel>"))

	@filter("numeric")
	def onNUMERIC(self, source, target, numeric, arg, message):

		if numeric == ERR_NICKNAMEINUSE:
			self.client.ircNICK(
					self.client.getNick() + "_")
		else:
			if arg is not None:
				self.lines.append(urwid.Text(
					"%s :%s" % (arg, message)))
			else:
				self.lines.append(urwid.Text(message))

		return True, None
	
	@filter("notice")
	def onNOTICE(self, source, target, message):
		if type(source) == str:
			nick = source
		else:
			nick, ident, host = sourceSplit(source)

		self.lines.append(urwid.Text(
				"-%s- %s" % (nick, message)))
		return True, None

	@filter("message")
	def onMESSAGE(self, source, target, message):
		if type(source) == str:
			nick = source
		else:
			nick, ident, host = sourceSplit(source)
		self.lines.append(urwid.Text(
				"<%s> %s" % (nick, message)))
		return True, None
	
	def cmdEXIT(self, message=""):
		if self.client.connected:
			self.cmdQUIT(message)
		raise SystemExit, 0

	def cmdSERVER(self, host, port=6667):
		self.client.open(host, int(port))
		self.client.ircUSER(
				self.client.getIdent(),
				socket.gethostname(),
				host,
				"PyMills Example IRC Client")
		self.client.ircNICK(self.client.getNick())

	def cmdSSLSERVER(self, host, port=6697):
		self.client.open(host, int(port), ssl=True)
		self.client.ircUSER(
				self.client.getIdent(),
				socket.gethostname(),
				host,
				"PyMills Example IRC Client")
		self.client.ircNICK(self.client.getNick())

	def cmdJOIN(self, channel):
		if self.channel is not None:
			self.cmdPART(self.channel, "Joining %s" % channel)

		self.client.ircJOIN(channel)
		self.channel = channel
	
	def cmdPART(self, channel=None, message="Leaving"):
		if channel is None:
			channel = self.channel
		if channel is not None:
			self.client.ircPART(channel, message)
			self.channel = None
		
	def cmdQUOTE(self, message):
		self.client.ircRAW(message)

	def cmdQUIT(self, message="Bye"):
		self.client.ircQUIT(message)

	def update_screen(self, size):
		self.body.set_focus(len(self.lines))
		canvas = self.top.render(size, focus=True)
		self.draw_screen(size, canvas)
	
def main():
	event = EventManager()
	client = Client(event)
	window = MainWindow(event, client)

	window.start()

	while True:
		try:
			if client.connected:
				client.process()
			window.process()
			event.flush()
		except KeyboardInterrupt:
			window.stop()
			break
		except SystemExit:
			window.stop()
			break
		except Exception, e:
			window.stop()
			print format_exc()
			break

	for i in xrange(len(event)):
		event.flush()

if __name__ == "__main__":
	main()
