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
from pymills.datatypes import OrderedDict

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
		return [Record(zip(fields, row)) for row in rows]

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

		NB:
			This returns a new cursor object and
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
					self._log.debug("Rows: %d" % self.getCursor().rowcount)
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

Connection = Session

class Record(OrderedDict):
	"""Record(data) -> a new multi-access record

	Create a new multi-access record given a list of 2-pair
	tuplies containing the field and value for that record.
	Each record created can be accessed in a dictionary-like
	fasion or using attribute names of the record object.
	"""

	def __init__(self, row):
		"initializes x; see x.__class__.__doc__ for signature"

		super(Record, self).__init__()

		for k, v in row:
			self.add(k, v)
	
	def add(self, k, v):
		"""R.add(k, v) -> None

		Add a new key and value given as k, v to this
		record.
		"""

		if type(k) == tuple:
			k = k[0]

		if type(v) == str:
			v = unicode(v, "utf-8")

		self[k] = v
		setattr(self, k, v)
	
	def remove(self, k):
		"""R.remove(k) -> None

		Remove a value given it's key from
		this record.
		"""		

		del self[k]
		del self.k

def pivot(rows, left, top, value):
	"""pivot(rows, left, top, value) -> rows

	Creates a cross-tab or pivot table from a normalised input
	rows. Use this unction to 'denormalize' a table of normalized
	records (rows).
	
	rows	- list of Record objects.
	left	- tuple of row headings
	top	- tuple of column headings
	"""

	rs = OrderedDict()
	ysort = []
	xsort = []
	for row in rows:
		yaxis = tuple([row[c] for c in left])
		if yaxis not in ysort: ysort.append(yaxis)
		xaxis = tuple([row[c] for c in top])
		if xaxis not in xsort: xsort.append(xaxis)
		try:
			rs[yaxis]
		except KeyError:
			rs[yaxis] = {}
		if xaxis not in rs[yaxis]:
			rs[yaxis][xaxis] = 0
		rs[yaxis][xaxis] += row[value]

	# Handle missing values
	for key in rs:
		if len(rs[key]) < len(xsort):
			for var in xsort:
				if var not in rs[key].keys():
					rs[key][var] = None

	headings = list(left)
	headings.extend(xsort)

	newRows = []

	for left in ysort:
		row = list(left)
		sortedkeys = rs[left].keys()
		sortedkeys.sort()
		sortedvalues = map(rs[left].get, sortedkeys)
		row.extend(sortedvalues)
		newRows.append(Record(zip(headings, row)))

	return newRows, sortedkeys

def variance(rows, names=("Variance", "Variance (%)",)):
	"""variance(rows, names=("Variance", "Variance (%)",)): -> rows

	Calculate a variance on a set of rows
	and add two new columns:
	 * Variance
	 * Variance (%)
	
	This function assumes that the data to calculate
	the variance on are the last two columns in the
	data set.
	"""

	newRows = []
	keys = rows[0].keys()[-2:]

	for row in rows:
		x = row[keys[0]]
		y = row[keys[1]]

		if None in [x, y]:
			d = None
			v = None
		else:
			d = y - x
			if x == 0:
				v = None
			else:
				v = d / x * 100

		newRow = Record(zip(row.keys(), row.values()))
		newRow.add(names[0], d)
		newRow.add(names[1], v)
		newRows.append(newRow)

	return newRows, names
