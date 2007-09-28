#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.event import listener, Component, Manager, \
		Event

class TodoList(Component):

	def __init__(self, *args):
		super(TodoList, self).__init__(*args)

		self.todos = {}

	def add(self, name, description):
		assert name not in self.todos, "To-do already in list"
		self.todos[name] = description
		self.push(
				Event(name, description),
				"TodoAdded")

class TodoPrinter(Component):

	@listener("TodoAdded")
	def onTodoAdded(self, name, description):
		print "TODO:", name
		print "	  ", description

def main():
	e = Manager()

	todo = TodoList(e)
	todo2 = TodoList(e)

	printer = TodoPrinter(e)
	printer2 = TodoPrinter(e)

	todo.add("Make coffee",
			"Really need to make some coffee")
	todo.add("Bug triage",
			"Double-check that all known issues were addressed")

	e.flush()

if __name__ == "__main__":
	main()
