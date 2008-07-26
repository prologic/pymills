#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, Component, Manager, Event

class TodoList(Component):

	todos = {}

	def add(self, name, description):
		assert name not in self.todos, "To-do already in list"
		self.todos[name] = description
		self.push(Event("Todo", name, description), "added")

class TodoPrinter(Component):

	@listener("added")
	def onADDED(self, name, description):
		print "TODO: %s" % name
		print "      %s" % description

def main():
	e = Manager()
	TodoPrinter(e)
	todo = TodoList(e)

	todo.add("Make coffee", "Really need to make some coffee")
	todo.add("Bug triage", "Double-check that all known issues were addressed")

	e.flush()

if __name__ == "__main__":
	main()
