# Filename: db.py
# Module:   db
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate$
# $Author$
# $Id$

"""Database Module"""

import string
import sqlite

class Error(Exception):
	pass

class SQLite:

	def __init__(self, database):
		try:
			self.__cx = sqlite.connect(database, autocommit=True)
			self.__cu = self.__cx.cursor()
		except sqlite.Error, e:
			raise Error("Could not open database -> %s" % e)
		
	def __del__(self):
		self.__cu.close()
		self.__cx.close()
	
	def select(self, fields, table, condition=None, limit=None):
		if not condition == None:
			if not limit == None:
				query = "SELECT %s FROM %s WHERE %s LIMIT %d;" % \
						(string.join(fields, ", "), table, condition, limit)
			else:
				query = "SELECT %s FROM %s WHERE %s;" % \
						(string.join(fields, ", "), table, condition)
		else:
			if not limit == None:
				query = "SELECT %s FROM %s LIMIT %d;" % \
						(string.join(fields, ", "), table, limit)
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
				records.append(record)
		return records

	def insert(self, table, fields, values):
		query = "INSERT INTO %s (%s) VALUES (\"%s\");" % \
				(table, string.join(fields, ", "), string.join(values, "\", \""))
		self.query(query)
	
	def delete(self, table, condition):
		query = "DELETE FROM %s WHERE %s;" % (table, condition)
		self.query(query)

	def query(self, sql):
		try:
			self.__cu.execute(sql)
			return self.__cu.fetchall()
		except sqlite.Error, e:
			raise Error("Error while executing query \"%s\": %s" % (sql, e))

class Records:

	def __init__(self):
		self._records = []
	
	def __getitem__(self, n):
		return self._records[n]

	def __setitem__(self, record):
		self._records.append(record)
	
	def append(self, record):
		self._records.append(record)
	
	def empty(self):
		return self._records == []

	def get(self, field, row = 0):
		if (not self.empty()) and (0 <= row < len(self._records)):
			record = self._records[row]
			return record[field]
		else:
			return None
