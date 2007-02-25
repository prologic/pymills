#!/usr/bin/env python

from pymills.irc import IRC
from pymills.event import EventManager, filter, listener
from pymills.sockets import TCPClient

class TestBot(TCPClient, IRC):

	def __init__(self, event):
		TCPClient.__init__(self, event)
		IRC.__init__(self)

	@filter()
	def onDEBUG(self, event):
		print event
		return False, event

	@listener("raw")
	def onRAW(self, data):
		self.write(data + "\r\n")

	@listener("read")
	def onREAD(self, line):
		TCPClient.onREAD(self, line)
		IRC.onREAD(self, line)

def main():

	event = EventManager()
	testbot = TestBot(event)

	testbot.open("localhost", 6667, ssl=True)

	testbot.ircUSER(
			"test",
			"localhost",
			"test.shortcircuit.net.au",
			"Test Bot")

	testbot.ircNICK("test")

	while True:
		if testbot.connected:
			testbot.process()
		event.flush()

if __name__ == "__main__":
	main()
