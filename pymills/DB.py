#!/usr/bin/env python

# Filename: DB.py
# Module:   DB
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-05-11 00:00:26 +1000 (Wed, 11 May 2005) $
# $Author: prologic $
# $Id: DB.py 1926 2005-05-10 14:00:26Z prologic $

"""DB

This is a database class containing simple interfaces to:
SQLite
MySQL
"""

__version__ = "0.1"
__copyright__ = "CopyRight (C) 2005 by James Mills"
__author__ = "James Mills <prologic@shortcircuit.net.au>"
__url__ = "http://shortcircuit.net.au/~prologic/"

import sqlite, string

class Records:

	def __init__(self):
		self._records = []
	
	def __getitem__(self, x):
		return self._records[x]

	def _add(self, record):
		self._records.append(record)
	
	def empty(self):
		return self._records == []

	def get(self, field, row = 0):
		if not self.empty() and row >= 0 and row < len(self._records):
			record = self._records[row]
			return record[field]
		else:
			return None

class SQLite:
	"SQLite Database Class"

	def __init__(self, database):
		"Initializes the database connection"

		self._cx = sqlite.connect(database, autocommit = True)
		self._cu = self._cx.cursor()
		
	def __del__(self):
		"Close the connection"

		self._cu.close()
		self._cx.close()
	
	def select(self, fields, table, condition = None, limit = None):
		"Select some data"

		if not condition == None:
			if not limit == None:
				query = "SELECT %s FROM %s WHERE %s LIMIT %d;" % (string.join(fields, ", "), table, condition, limit)
			else:
				query = "SELECT %s FROM %s WHERE %s;" % (string.join(fields, ", "), table, condition)
		else:
			if not limit == None:
				query = "SELECT %s FROM %s LIMIT %d;" % (string.join(fields, ", "), table, limit)
			else:
				query = "SELECT %s FROM %s;" % (string.join(fields, ", "), table)

		rows = self.query(query)
		records = Records()
		if not rows == None:
			for row in rows:
				record = {}
				for i, field in enumerate(fields):
					tokens = field.split(" ")
					if len(tokens) == 3:
						field = tokens[2]
					record[field] = row[i]
				records._add(record)
		return records

	def insert(self, table, fields, values):
		query = "INSERT INTO %s (%s) VALUES (%s);" % (table, string.join(fields, ", "), string.join(values, ", "))
		self.query(query)
	
	def delete(self, table, condition):
		query = "DELETE FROM %s WHERE %s;" % (table, condition)
		self.query(query)

	def query(self, sql):
		"Execute a query"

		try:
			self._cu.execute(sql)
			return self._cu.fetchall()
		except sqlite.Error, e:
			print "ERROR: %s" % str(e)
			print "SQL: %s" % sql

#" vim: tabstop=3 nocindent autoindent
