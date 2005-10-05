# Filename: db.py
# Module:   db
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate$
# $Author$
# $Id$

"""Database Module"""

import string
from pysqlite2 import dbapi2 as sqlite

class Error(Exception):
	pass

class SQLite:

	def __init__(self, database, debug=False):
		self._debug = debug
		try:
			self.__cx = sqlite.connect(database)
			self.__cu = self.__cx.cursor()
		except sqlite.Error, e:
			raise Error("Could not open database -> %s" % e)
		
	def __del__(self):
		self.__cx.commit()
		self.__cu.close()
		self.__cx.close()
	
	def _quote(self, s):
		return s.replace('"', '\"')

	def _quoteAll(self, list):
		return map(self._quote, list)

	def select(self, fields, table, condition=None, order=None, limit=None):
		query = "SELECT %s FROM %s" % \
				(string.join(fields, ", "), table)
		if condition is not None:
			query = "%s WHERE %s" % (query, condition)
		if order is not None:
			query = "%s ORDER BY %s" % (query, order)
		if limit is not None:
			query = "%s LIMIT %d" % (query, limit)
		query = "%s;" % query

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
		values = self._quoteAll(values)
		query = "INSERT INTO %s (%s) VALUES (\"%s\");" % \
				(table, string.join(fields, ", "), string.join(values, "\", \""))
		self.query(query)
	
	def delete(self, table, condition):
		query = "DELETE FROM %s WHERE %s;" % (table, condition)
		self.query(query)

	def query(self, sql):
		if self._debug:
			print "Query: %s" % sql
		try:
			sql = sql.replace('"', '\"')
			self.__cu.execute(self._quote(sql))
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
