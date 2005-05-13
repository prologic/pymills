# Filename: db.py
# Module:   db
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-05-11 00:00:26 +1000 (Wed, 11 May 2005) $
# $Author: prologic $
# $Id: db.py 1926 2005-05-10 14:00:26Z prologic $

"""Database Module

This module contains classes that provide interfaces to the
MySQL and SQLite databases.
"""

import string

import sqlite

class Error(Exception):
	"""Error Class

	Used to raise exceptions upon erors
	"""

	pass

class SQLite:
	"""SQLite Database Class

	This class provides an interface to the SQLite database.

	Example:
	>>> import db
	>>> db = db.SQLite("test.db")
	>>> db.query("CREATE TABLE foo (first TEXT, last TEXT);")
	[]
	>>> db.insert("foo", ["first", "last"], ["James", "Mills"])
	>>> records = db.select(["first", "last"], "foo")
	>>> records.get("first")
	'James'
	"""

	def __init__(self, database):
		"""Initializes
		
		Setup the connection to teh database (a file for SQLite)

		Args:
		   database : string of the database filename
		"""

		try:
			self.__cx = sqlite.connect(database, autocommit=True)
			self.__cu = self.__cx.cursor()
		except sqlite.Error, e:
			raise Error("Could not open database -> %s" % e)
		
	def __del__(self):
		"""Close the connection"""

		self.__cu.close()
		self.__cx.close()
	
	def select(self, fields, table, condition=None, limit=None):
		"""Select some data

		This uses SELECT to select some rows of data from the
		database given the fields, table, condition and limit.

		Args:
		   fields : list of fields to select
		   table : string of table to select from
		   condition : string containing the condition
		   limit : int specifying the limit (no. of rows)

		Returns:
		   Object (instance of _Records)
		"""

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
		records = _Records()
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
		"""Insert some data

		This uses INSERT to insert a row of data into the
		database given by the fields, table and values.

		Args:
		   table : string of table to insert into
		   fields : list of fields to insert
		   values : list of values to insert

		Returns:
		   None
		"""

		query = "INSERT INTO %s (%s) VALUES (\"%s\");" % \
				(table, string.join(fields, ", "), string.join(values, "\", \""))
		self.query(query)
	
	def delete(self, table, condition):
		"""Deletes some data

		This uses DELETE to delete a row of data from the
		database given by the table and condition.

		Args:
		   table : string of table to delete from
		   condition : string containing the condition

		Returns:
		   None
		"""

		query = "DELETE FROM %s WHERE %s;" % (table, condition)
		self.query(query)

	def query(self, sql):
		"""Execute a query

		This executes the query in sql, this can be any query
		that is valid SQL.

		Args:
		   sql : string of the sql query to be executed

		Returns:
		   list (list of uples)
		"""

		try:
			self.__cu.execute(sql)
			return self.__cu.fetchall()
		except sqlite.Error, e:
			raise Error("Error while executing query \"%s\": %s" % (sql, e))

class _Records:
	"""Records Class

	A class that holds a number of records from a
	SELECT query
	This is used internally.
	"""

	def __init__(self):
		"""Initialize"""

		self._records = []
	
	def __getitem__(self, n):
		return self._records[n]

	def __setitem__(self, record):
		self._records.append(record)
	
	def append(self, record):
		"""Add a record onto the end of the list

		Args:
		   record : dict of the record

		Returns:
		   None
		"""

		self._records.append(record)
	
	def empty(self):
		"""Return True if records is empty"""

		return self._records == []

	def get(self, field, row = 0):
		"""Return a value from a record

		Given a field and row, return the value for that row
		and field.

		Args:
		   field : string of the field to return
		   row : int row number to get the value from

		Returns:
		   string os None
		"""

		if (not self.empty()) and (0 <= row < len(self._records)):
			record = self._records[row]
			return record[field]
		else:
			return None
