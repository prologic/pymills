#!/usr/bin/env python

import Core

def test():

	testBot = Core.Bot()
	testBot.addPlugin(Hello)

	testBot.ircSERVER("dede.mills", 6667)
	testBot.ircUSER("testbot", "", "dede.mills", "Test Bot")
	testBot.ircNICK("testbot")
	testBot.ircJOIN("#se")

	testBot.run()

if __name__ == "__main__":
	test()
