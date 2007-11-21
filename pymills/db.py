# Filename: db.py
# Module:	db
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

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
 * MySQL
 * Oracle

Example Usage:
>>> import db
>>> data = db.Session("sqlite://test.db")
>>> data.do("create table names (firstname, lastname)")
[]
>>> data.do("insert into names values ('James', 'Mills')")
[]
>>> data.do("insert into names values ('Danny', 'Rawlins')")
[]
>>> data.do("select firstname, lastname from names")
[{'lastname': u'Mills', 'firstname': u'James'}, {'lastname': u'Rawlins', 'firstname': u'Danny'}]
>>> rows = data.do("select firstname, lastname from names")
>>> rows[0]
{'lastname': u'Mills', 'firstname': u'James'}
>>> rows[0]["firstname"]
u'James'
>>> rows[0].lastname
u'Mills'
"""

from time import time

from pymills.misc import duration
from pymills.types import OrderedDict

def _parseURI(uri):
	"""_parseURI(uri) -> dict

	Parse a URI into it's parts returning
	a dictionary of schema, username, password and location.
	If this fails, {} is returned.
	"""

	import re

	m = re.match("(?P<schema>oracle|mysql|sqlite)://"
			"((?P<username>.*?):(?P<password>.*?)@(?P<hostname>.*?)/)?"
			"(?P<database>.*)",
			uri, re.IGNORECASE)
	if m is not None:
		return m.groupdict()
	else:
		raise DBError("Supplied URI is not valid: %s" % uri)

class DBError(Exception): pass

class Session(object):
	"""Session(uri) -> new database session

	Create a new session object to the database specified
	by the uri.
	"""

	def __init__(self, uri, log=None, dryrun=False, debug=False):
		"initializes x; see x.__class__.__doc__ for signature"

		self._log = log
		self._dryrun = dryrun
		self._debug = debug

		if self._dryrun and (self._log is not None):
			self._log.info("dryrun mode enabled")

		self._cx = None
		self._cu = None

		for k, v in _parseURI(uri).iteritems():
			setattr(self, "_%s" % k, v)

		if self._schema.lower() == "oracle":
			try:
				import cx_Oracle as oracle
			except:
				raise DBError("No Oracle support available.")

			try:
				self._cx = oracle.connect(
						dsn=self._hostname,
						user=self._username,
						password=self._password)
				self._cu = self._cx.cursor()
			except Exception, e:
				raise DBError("Could not open connection: %s" % str(e))

		elif self._schema.lower() == "mysql":
			try:
				import MySQLdb as mysql
			except:
				raise DBError("No MySQL support available.")

			try:
				self._cx = mysql.connect(
						host=self._hostname,
						user=self._username,
						passwd=self._password,
						db=self._database)
				self._cu = self._cx.cursor()
			except Exception, e:
				raise DBError("Could not open database: %s" % e)

		elif self._schema.lower() == "sqlite":
			try:
				import sqlite3 as sqlite
			except:
				raise DBError("No SQLite support available.")

			if self._database.lower() == ":memory:":
				filename = ":memory:"
			else:
				import os
				filename = os.path.abspath(
						os.path.expanduser(self._database))

			try:
				self._cx = sqlite.connect(filename)
				self._cu = self._cx.cursor()
			except sqlite.Error, e:
				raise DBError("Could not open database '%s' -> %s" % (filename, e))

	def __del__(self):
		"""uninitializes x

		Perform a last commit and close the connection to the
		database.
		"""

		try:
			if not self._dryrun:
				self._cx.commit()
			self._cu.close()
			self._cx.close()
		except:
			pass

	def __getFields__(self):
		"""C.__getFields__() -> [field1, field2, ...]

		Get a list of field names for the current result set
		stored in the cursor's .description. If there are
		no fields [] is returned.
		"""

		if self._cu.description is not None:
			return map(lambda x: x[0], self._cu.description)
		else:
			return []

	def __buildResult__(self, fields):
		"""C.__buildResult__(fields) -> list of rows from cursor

		Build a list of rows where each row is an instance
		of Record. The rows returned are retrieved from the
		last transaction executed and stored in the cursor.
		"""

		rows = self._cu.fetchall()
		return [_Record(zip(fields, row)) for row in rows]

	def commit(self):
		"""C.commit() -> None

		Perform a manual commit.
		"""

		if not self._dryrun:
			if self._debug and (self._log is not None):
				self._log.debug("Commiting to database...")
			self._cx.commit()

	def execute(self, sql, *args, **kwargs):
		"""C.execute(sql, *args, **kwargs) -> list of rows, or []

		Execute the given SQL statement in sql and return
		a list of rows (if appropiate) or return an empty list.
		If this fails, a DBError exception will be raised.
		"""

		try:
			if not self._dryrun:
				if self._debug and (self._log is not None):
					st = time()
					self._log.debug("SQL: %s Args: %s kwArgs: %s" % (
						sql,
						str(args),
						str(kwargs)))
				self._cu.execute(sql, *args, **kwargs)
				fields = self.__getFields__()
				if fields == []:
					r = []
				else:
					r = self.__buildResult__(fields)
				if self._debug and (self._log is not None):
					et = time()
					self._log.debug("Result: %s" % str(r))
					if (et - st) < 1:
						self._log.debug("Time: %0.2f" % (et - st))
					else:
						self._log.debug("Time: %s+%s:%s:%s" % duration(et - st))
				return r
			else:
				if self._debug and (self._log is not None):
					self._log.debug("SQL: %s Args: %s kwArgs: %s" % (
						sql,
						str(args),
						str(kwargs)))
				return []
		except Exception, e:
			raise
			raise DBError("Error while executing query \"%s\": %s" % (sql, e))
	
	def do(self, sql, *args, **kwargs):
		"""Synonym of execute"""

		return self.execute(sql, *args, **kwargs)

Connection = Session

class _Record(OrderedDict):
	"""_Recird(row) -> a new multi-access row

	Create a new multi-access row given a list of 2-pair
	tuplies containing the field and value for that row.
	Each row created can be access any number of ways.
	"""

	def __init__(self, row):
		OrderedDict.__init__(self)
		for k, v in row:
			if type(v) == str:
				v = unicode(v, "utf-8")
			self[k] = v
			setattr(self, k, v)
