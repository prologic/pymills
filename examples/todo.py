#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, Component, Manager, \
		Event

class TodoList(Component):

	def __init__(self, *args):
		self.todos = {}

	def add(self, name, description):
		assert name not in self.todos, "To-do already in list"
		self.todos[name] = description
		self.event.push(
				Event(name, description),
				"TodoAdded")

class TodoPrinter(Component):

	@listener("TodoAdded")
	def onTodoAdded(self, name, description):
		print "TODO:", name
		print "	  ", description

def main():
	manager = Manager()

	todo = TodoList(manager)
	todo2 = TodoList(manager)
	assert id(todo) == id(todo2)

	printer = TodoPrinter(manager)
	printer2 = TodoPrinter(manager)
	assert id(printer) == id(printer2)

	todo.add("Make coffee",
			"Really need to make some coffee")
	todo.add("Bug triage",
			"Double-check that all known issues were addressed")

	manager.flush()

if __name__ == "__main__":
	main()
