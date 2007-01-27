# Filename: csv.py
# Module:   csv
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""CSV

This Class handles and parses CSV files to other formats.
Currently it can export to the SQLite format as a schema.
"""

import re
import sys
import string

class CSV:

	def __init__(self, file, create = False, seperator = ", "):
		"""Initialize Object

		file      - (string)  Name of CSV file to open
		create    - (boolean) Attempt to create table if True
		seperator - (string)  Value Delimiter
		"""

		try:
			self.fd = open(file, "r")
		except IOError, e:
			if e[0] == 2:
				print "ERROR: Could not open CSV file: " + file
				sys.exit(2)
			else:
				print "ERROR:", e
				sys.exit(2)
		self.table = file.split(".")[0]
		self.lines = []
		self.create = create
		self.seperator = seperator
		self.process()
	
	def process(self):
		"Loads the open CSV file into a list of lines"

		for line in self.fd:
			self.lines.append(line)
	
	def toSQL(self):
		"Convert the CSV file to SQL statements"

		if self.create:
			line = self.lines.pop(0)
			fields = line.split(self.seperator)
			print "CREATE TABLE " + self.table + "(",
			print string.join(fields, ", "),
			print ");"
		id = 0
		for line in self.lines:
			values = re.split(r"(?<!\\)" + self.seperator, line)
			values = map(repr, values)

			values.insert(0, str(id))
			id = id + 1

			print "INSERT INTO " + self.table + " VALUES (",
			print string.join(values, ", "),
			print ");"
