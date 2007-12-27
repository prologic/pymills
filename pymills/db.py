# Module:	db
# Date:		4th August 2004
# Author:	James Mills, prologic at shortcircuit dot net dot au

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
>>> from pymills.db import newDB
>>> db = newDB("sqlite://test.db")
>>> db.do("create table names (firstname, lastname)")
[]
>>> db.do("insert into names values ('James', 'Mills')")
[]
>>> db.do("insert into names values ('Danny', 'Rawlins')")
[]
>>> db.do("select firstname, lastname from names")
[{'lastname': u'Mills', 'firstname': u'James'}, {'lastname': u'Rawlins', 'firstname': u'Danny'}]
>>> rows = db.do("select firstname, lastname from names")
>>> rows[0]
{'lastname': u'Mills', 'firstname': u'James'}
>>> rows[0]["firstname"]
u'James'
>>> rows[0].lastname
u'Mills'
"""


from pymills.misc import duration
from pymills.types import OrderedDict

def newDB(s, **kwargs):
	"""newDB(s) -> new session object

	Create a new database session object from the
	given string s representing a dadtabase URI.
	An optional list of keyword arguments can be
	passed to affect how the session object is
	created:
	 * log    - logger instnace
	 * debug  - wether or not debug mode is enabled
	 * dryrun = whether or not drrun mode is enabled
	 """

	d = __parseURI(s)
	schema = d["schema"]
	username = d["username"]
	password = d["password"]
	hostname = d["hostname"]
	database = d["database"]

	if schema.lower() == "oracle":
		try:
			import cx_Oracle as oracle
		except:
			raise DBError("No Oracle support available.")

		try:
			return OracleSession(oracle.connect(
				dsn=hostname, user=username,
				password=password), **kwargs)
		except Exception, e:
			raise DBError("Could not open connection: %s" % str(e))

	elif schema.lower() == "mysql":
		try:
			import MySQLdb as mysql
		except:
			raise DBError("No MySQL support available.")

		try:
			return MySQLSession(mysql.connect(
				host=hostname,	user=username,
				passwd=password, db=database), **kwargs)
		except Exception, e:
			raise DBError("Could not open database: %s" % e)

	elif schema.lower() == "sqlite":
		try:
			import sqlite3 as sqlite
		except:
			raise DBError("No SQLite support available.")

		if database.lower() == ":memory:":
			filename = ":memory:"
		else:
			import os
			filename = os.path.abspath(
					os.path.expanduser(database))

		try:
			return SQLiteSession(
					sqlite.connect(filename), **kwargs)
		except sqlite.Error, e:
			raise DBError("Could not open database '%s' -> %s" % (filename, e))
	
	else:
		raise DBError("Unsupported schema: %s" % schema)

def __parseURI(s):
	"""__parseURI(s) -> dict

	Parse the given string s representing a database URI
	and return a dictionary of it's parts. Return the
	schema, username, password, filename or hostname
	and an optional database name.

	The following syntax is recognized:
	 sqlite:///path/to/foo.db or sqlite://:memory:
	 mysql://username:password@hostname/database
	 oracle://username:password@tns/
	"""

	import re

	m = re.match("(?P<schema>oracle|mysql|sqlite)://"
			"((?P<username>.*?):(?P<password>.*?)@(?P<hostname>.*?)/)?"
			"(?P<database>.*)",
			s, re.IGNORECASE)
	if m is not None:
		return m.groupdict()
	else:
		raise DBError("Supplied URI is not valid: %s" % s)

class DBError(Exception):
	pass

class BaseSession(object):
	"""BaseSession(cx) -> new database session

	Create a new session object to the database connection
	specified. Optional keyword argumnets can be passed
	to enable logging, debug mode and dryrun mode.
	"""

	def __init__(self, cx, log=None, dryrun=False, debug=False):
		"initializes x; see x.__class__.__doc__ for signature"

		self._cx = cx
		self._log = log
		self._dryrun = dryrun
		self._debug = debug

		if self._dryrun and (self._log is not None):
			self._log.info("dryrun mode enabled")

		self._cu = self.newCursor()

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
		return [Record(zip(fields, row)) for row in rows]

	def __execute__(self, sql=None, *args, **kwargs):
		"""C.__execute__(sql=None, *args, **kwargs) -> list of rows, or []

		Execute the given SQL statement or a previously prepared
		statement in the current internal cursor.

		NOTE:
		 * This is a dummy implementation.
		 * Sub-classes _must_ implement this specifically
		   for the database type.
		"""

		pass

	def commit(self):
		"""C.commit() -> None

		Perform a manual commit.
		"""

		if not self._dryrun:
			if self._debug and (self._log is not None):
				self._log.debug("Commiting to database...")
			self._cx.commit()

	def newCursor(self):
		"""C.newCursor() -> new cursor object

		Return a new db-api cursor object. Useful
		for performing other functions this library
		doesn't wrap around or support.
		eg: callproc (Oracle)

		NB: This returns a new cursor object and
		    does not return the current internal one.
			 Use getCursor to get a copy of the
			 internal one.
		"""

		return self._cx.cursor()

	def getCursor(self):
		"""C.getCursor() -> cursor object

		Return the db-api internal cursor
		object. Useful for performing other
		functions this library doesn't wrap
		around or support. eg: callproc (Oracle)
		"""

		return self._cu

	def execute(self, sql=None, *args, **kwargs):
		"""C.execute(sql=None, *args, **kwargs) -> list of rows, or []

		Execute the given SQL statement or a previously prepared
		statement in the current internal cursor. Return a list of rows
		if any or return an empty list.
		If this fails, a DBError exception will be raised.
		"""

		from time import time

		try:
			if not self._dryrun:
				if self._debug and (self._log is not None):
					st = time()
					self._log.debug("SQL: %s Args: %s kwArgs: %s" % (
						sql,
						str(args),
						str(kwargs)))
				self.__execute__(sql, *args, **kwargs)
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

	def do(self, sql=None, *args, **kwargs):
		"""Synonym of execute"""

		return self.execute(sql, *args, **kwargs)

class SQLiteSession(BaseSession):

	def __execute__(self, sql=None, *args, **kwargs):
		self._cu.execute(sql, args)

class MySQLSession(BaseSession):

	def __execute__(self, sql=None, *args, **kwargs):
		self._cu.execute(sql, args)

class OracleSession(BaseSession):

	def __execute__(self, sql=None, *args, **kwargs):
		self._cu.execute(sql, *args, **kwargs)

Connection = newDB

class Record(OrderedDict):
	"""Recird(row) -> a new multi-access row

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
