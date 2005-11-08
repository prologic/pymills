# Filename: db.py
# Module:	db
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""OO SQL RDBM Layer

This is an Object Oriented SQL RDBM Layer to make the use of
SQL RDBMs such as MySQL, SQLite easier to use.

Supports RDBMs:
	SQLite

More to come soon...
"""

import os
import string
from pysqlite2 import dbapi2 as sqlite

class Error(Exception):
	pass

class SQLite:

	def __init__(self, conn, debug=False):
		self._debug = debug

		try:
			self._cx = sqlite.connect(
					os.path.abspath(
						os.path.expanduser(
							conn)))
			self._cu = self._cx.cursor()

		except sqlite.Error, e:
			raise Error("Could not open connection -> %s" % e)
		
	def __del__(self):
		try:
			self._cx.commit()
			self._cu.close()
			self._cx.close()
		except:
			pass
	
	def update(self):
		self._cx.commit()
	
	def execute(self, sql):
		if self._debug:
			print "Query: %s" % sql
		try:
			self._cu.execute(sql)
			return self._cu.fetchall()
		except sqlite.Error, e:
			raise Error("Error while executing query \"%s\": %s" % (sql, e))
	
class SQLObject:

	def __init__(self, conn, table=None, fields=None):
		self._conn = conn
		self._table = table
		self._fields = fields

	def _quote(self, s):
		if type(s) is str:
			return s.replace('"', '\"')
		else:
			return s

	def setTable(self, table):
		self._table = table
	
	def setFields(self, fields):
		self._fields = fields

	def select(self, condition=None, order=None, limit=None,
			table=None, fields=None):

		if table is None and (self._table is not None):
			table = self._table
		elif table is not None:
			pass
		else:
			raise Error("No table given")

		if fields is None and (self._fields is not None):
			fields = self._fields
		elif fields is not None:
			pass
		else:
			raise Error("No fields given")
		
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
		records = Records(self)
		if not rows == None:
			for row in rows:
				record = {}
				for i, field in enumerate(fields):
					tokens = field.split(" ")
					if len(tokens) == 3:
						field = tokens[2]
					if row[i] is None:
						record[field] = Null()
					else:
						record[field] = row[i]
				records.append(record)
		return records

	def insert(self, values, table=None, fields=None):

		if table is None and (self._table is not None):
			table = self._table
		elif table is not None:
			pass
		else:
			raise Error("No table given")

		if fields is None and (self._fields is not None):
			fields = self._fields
		elif fields is not None:
			pass
		else:
			raise Error("No fields given")
		
		values = map(self._quote, map(str, values))
		query = "INSERT INTO %s (%s) VALUES (\"%s\");" % \
				(table, string.join(fields, ", "), string.join(values, "\", \""))
		self.query(query)
		self._conn.update()
	
	def delete(self, condition, table=None, fields=None):

		if table is None and (self._table is not None):
			table = self._table
		elif table is not None:
			pass
		else:
			raise Error("No table given")

		if fields is None and (self._fields is not None):
			fields = self._fields
		elif fields is not None:
			pass
		else:
			raise Error("No fields given")
		
		query = "DELETE FROM %s WHERE %s;" % (table, condition)
		self.query(query)
		self._conn.update()

	def update(self, condition, values, 
			table=None, fields=None):

		if table is None and (self._table is not None):
			table = self._table
		elif table is not None:
			pass
		else:
			raise Error("No table given")

		if fields is None and (self._fields is not None):
			fields = self._fields
		elif fields is not None:
			pass
		else:
			raise Error("No fields given")

		if not len(fields) == len(values):
			raise Error("Number of fields and values don't match!")
	
		tmp = ""
		for i, field in enumerate(fields):
			if i < (len(fields) - 1):
				tmp += "%s=\"%s\", " % (field, values[i])
			else:
				tmp += "%s=\"%s\"" % (field, values[i])

		query = "UPDATE %s SET %s " % (table, tmp)
		if condition is not None:
			query += " WHERE %s" % condition
		
		self.query(query)
		self._conn.update()

	def query(self, sql):
		sql = sql.replace('"', '\"')
		return self._conn.execute(self._quote(sql))

class Null:

	def __str__(self):
		return "NULL"

	def __repr__(self):
		return "NULL"

class Records:

	def __init__(self, db):
		self._db = db
		self._records = []
	
	def __repr__(self):
		from StringIO import StringIO
		f = StringIO()
		for i, record in enumerate(self._records):
			f.write("Record: %d\n" % i)
			for key, value in record.iteritems():
				f.write("   %s = %s\n" % (key, value))
		output = f.getvalue()
		f.close()
		return output
			
	def __len__(self):
		return len(self._records)

	def __getitem__(self, n):
		return self._records[n]

	def __setitem__(self, x):
		pass
	
	def append(self, record):
		self._records.append(record)
	
	def empty(self):
		return self._records == []

	def set(self, field, value, row=0):
		record = self._records[row]
		condition = ""
		for i, (k, v) in enumerate(record.iteritems()):
			if i < (len(record) - 1):
				condition += "%s = \"%s\" AND " % (k, v)
			else:
				condition += "%s = \"%s\"" % (k, v)
		self._db.update(condition, [value], None, [field])
		record[field] = value

	def get(self, field, row=0):
		if (not self.empty()) and (0 <= row < len(self._records)):
			record = self._records[row]
			return record[field]
		else:
			return Null()
