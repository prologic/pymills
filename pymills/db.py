# Filename: db.py
# Module:	db
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Database Library

Library to assist in the creation of applications that
require access to Relational Database Management Systems
such as MySQL and SQLite.

NOTE: This library is not an Object Relational Mapper, it is
simply a library that hides some of the interfaces of the 
Python DB API and gives you nicer access to results
with multiple access interfaces. (See example below)

Supprted:
* SQLite

Example Usage:
>>> import db
>>> conn = db.Connection("sqlite://test.db")
>>> conn.execute("create table names (firstname, lastname)")
[]
>>> conn.execute("insert into names values ('James', 'Mills')")
[]
>>> conn.execute("insert into names values ('Danny', 'Rawlins')")
[]
>>> conn.execute("select firstname, lastname from names")
[{'lastname': u'Mills', 'firstname': u'James'}, {'lastname': u'Rawlins', 'firstname': u'Danny'}]
>>> rows = conn.execute("select firstname, lastname from names")
>>> rows[0]
{'lastname': u'Mills', 'firstname': u'James'}
>>> rows[0]["firstname"]
u'James'
>>> rows[0].lastname    
u'Mills'
"""

import os
import re
from datatypes import OrderedDict

try:
	from pysqlite2 import dbapi2 as sqlite
except ImportError:
	pass

try:
	from MySQLdb import dbapi2 as mysql
except ImportError:
	pass

def parseURI(uri):
	"""uri -> {"schema": ..., "username": ..., ...}

	Parse a Connection URI into it's parts returning
	a dictionary of schema, username, password and location.
	If this fails, {} is returned.
	"""

	m = re.match("(?P<schema>mysql|sqlite)://"
			"((?P<username>.*?):(?P<password>.*?)@)?"
			"(?P<location>.*)",
			uri, re.IGNORECASE)
	if m is not None:
		return m.groupdict()
	else:
		return {}

class DBError(Exception):
	"""Database Error Occured"""

	pass

class Connection:
	"""Connection(uri) -> new connection

	Create a new connection object to the database specified
	by the uri.
	"""

	def __init__(self, uri):
		"initializes x; see x.__class__.__doc__ for signature"

		self._cx = None
		self._cu = None

		for k, v in parseURI(uri).iteritems():
			setattr(self, "_%s" % k, v)

		if self._schema.lower() == "mysql":
			raise NotImplemented

		elif self._schema.lower() == "sqlite":
			try:
				self._cx = sqlite.connect(
						os.path.abspath(
							os.path.expanduser(self._location)))
				self._cu = self._cx.cursor()
			except sqlite.Error, e:
				raise DBError("Could not open connection -> %s" % e)

	def __del__(self):
		"""uninitializes x

		Perform a last commit and close the connection to the
		database.
		"""

		try:
			self._cx.commit()
			self._cu.close()
			self._cx.close()
		except:
			pass

	def _getFields(self, sql):
		"""sql -> ["...", ...]

		Parses the given sql statement extracting the fields
		used in a SELECT statement returning these fields
		as a list. If no fields are found, an empty list is
		returned.
		"""

		m = re.match("SELECT *(.*) *FROM.*", sql, re.IGNORECASE)
		if m is not None:
			return map(lambda s: s.strip(), m.group(1).strip().split(","))
		else:
			return []
	
	def _buildResult(self, fields):
		"""C.__buildResult(fields) -> list of rows from cursor

		Build a list of rows where each row is an instance
		of Record. The rows returned are retrieved from the
		last transaction executed and stored in the cursor.
		"""

		return [Record(zip(fields, row)) for row in self._cu.fetchall()]
	
	def setAutoCommit(self, autocommit=True):
		"""C.setAutoCommit(autocommit) -> None

		Set the autocommit flag of the connection.
		If enabled (autocommit=True), then a commit will occur
		each time a transaction is executed. This can hamper
		performance a little.
		"""

		self.cx.autocommit = autocommit

	def commit(self):
		"""C.commit() -> None

		Perform a manual commit.
		"""

		self._cx.commit()
	
	def execute(self, sql):
		"""C.execute(sql) -> list of rows, or []

		Execute the given SQL statement in sql and return
		a list of rows (if appropiate) or return an empty list.
		If this fails, a DBError exception will be thrown.
		"""

		sql = sql.strip()

		if re.match("SELECT.*", sql, re.IGNORECASE) is not None:
			fields = self._getFields(sql)
		else:
			fields = []

		try:
			self._cu.execute(sql)
			if not fields == []:
				return self._buildResult(fields)
			else:
				return []
		except sqlite.Error, e:
			raise DBError("Error while executing query \"%s\": %s" % (sql, e))
	
	def do(self, sql):
		"""Synonym of execute"""

		return self.execute(sql)

class Record(OrderedDict):
	"""Recird(row) -> a new multi-access row

	Create a new multi-access row given a list of 2-pair
	tuplies containing the field and value for that row.
	Each row created can be access any number of ways.

	Example:
	>>> row = db.Record([("a", 1), ("b", 2), ("c", 3)])
	>>> row.a
	1
	>>> row["a"]
	1
	"""

	def __init__(self, row):
		OrderedDict.__init__(self)
		for k, v in row:
			self[k] = v
			setattr(self, k, v)
