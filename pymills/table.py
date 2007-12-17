# Module:	table
# Date:		17th December 2007
# Author:	James Mills, James dot Mills at au dot pwc dot com

"""Table generation, display and manipulation module.

Classes to generate ASCII and HTML tables and traverse
data.
"""

import types
from StringIO import StringIO

class Header(object):
	"""Header(name, **kwargs) -> new table header object

	Container class that holds the definition of a table
	header and how each piece of data should be formatted
	and displayed.

	An Optional list of kwargs can also be supplied that
	affect how this header is created:
	 * type   - the data type. Must be compatible with type(x)
	 * align  - text alignment. one of "left", "center", or "right"
	 * hidden - whether this column of data and header is displayed.
	 * format - format str or callable used to format cells
	 * width  - width to use when formatting strings by __str__ (used by align)
	 * cls    - class attribute used by toHTML
	 * style  - style attribute used by toHTML
	 * ccls   - cell class attribute to use for each cell used by toHTML
	 * cstyle - cell style attribute to use for each cell used by toHTML

	Example
	-------
	>>> h = Header("Test")
	>>> print h
	Test
	>>> print h.toHTML()
	<th>Test</th>
	>>>
	"""

	def __init__(self, name, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		self.name = name

		self.type = kwargs.get("type", str)
		self.align = kwargs.get("align", None)
		self.format = kwargs.get("format", "%s")
		self.width = kwargs.get("width", len(self.name))
		self.cls = kwargs.get("cls", None)
		self.style = kwargs.get("style", None)
		self.ccls = kwargs.get("ccls", None)
		self.cstyle = kwargs.get("cstyle", None)

	def __str__(self):
		if self.align:
			width = self.width
			if self.align == "left":
				return self.name.ljust(widtH)
			elif self.align == "center":
				return self.name.center(widtH)
			elif self.align == "right":
				return self.name.rjust(widtH)
			else:
				return self.name.ljust(width)
		else:
			return self.name
	
	def toHTML(self):
		align, cls, style = ("",) * 3
		if self.align:
			align = "align=\"%s\"" % self.align
		if self.cls:
			cls = "class=\"%s\"" % self.cls
		if self.style:
			style = "style=\"%s\"" % self.style
		attrs = " ".join([align, cls, style]).strip()
		if attrs == "":
			return "<th>%s</th>" % self.name
		else:
			return "<th %s>%s</th>" % (attrs, self.name)

class Row(object):
	"""Row(cells, **kwargs) -> new table row object

	Container class that holds the definition of a table
	row and a set of cells and how each cell should be
	formatted and displayed.

	An Optional list of kwargs can also be supplied that
	affect how this row is created:
	 * hidden - whether this row is displayed.
	 * cls    - class attribute used by toHTML
	 * style  - style attribute used by toHTML

	Example
	-------
	>>> c = Cell(22.0/7.0, format="%0.2f", align="right", cls="foo", style="hidden: true")
	>>> r = Row([c], cls="asdf", style="qwerty")
	>>> print r
	3.14
	>>> print r.toHTML()
	<tr class="asdf" style="qwerty"><td align="right" class="foo" style="hidden: true">3.14</td></td>
	>>>
	"""

	def __init__(self, cells, row=None, header=None, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		self.cells = cells

		self.hidden = kwargs.get("hidden", False)
		self.cls = kwargs.get("cls", None)
		self.style = kwargs.get("style", None)

	def __str__(self):
		if self.hidden:
			return ""
		else:
			return "".join([str(cell) for cell in self.cells])

	def toHTML(self):
		if self.hidden:
			return ""
		else:
			cls, style = ("",) * 2
			if self.cls:
				cls = "class=\"%s\"" % self.cls
			if self.style:
				style = "style=\"%s\"" % self.style
			attrs = " ".join([cls, style]).strip()

			cells = "".join([cell.toHTML() for cell in self.cells])
			if attrs == "":
				return "<tr>%s</tr>" % cells
			else:
				return "<tr %s>%s</td>" % (attrs, cells)

class Cell(object):
	"""Cell(value, row=None, header=None, **kwargs) -> new table cell object

	Container class that holds the definition of a table
	cell and it's value and how it should be formatted
	and displayed.

	An Optional list of kwargs can also be supplied that
	affect how this header is created:
	 * type   - the data type. Must be compatible with type(x)
	 * align  - text alignment. one of "left", "center", or "right"
	 * format - format str or callable
	 * cls    - class attribute used by toHTML
	 * style  - style attribute used by toHTML

	Example
	-------
	>>> c = Cell(22.0/7.0, format="%0.2f", align="right", cls="foo", style="hidden: true")
	>>> print c
	3.14
	>>> print c.toHTML()
	<td align="right" class="foo" style="hidden: true">3.14</td>
	>>>
	"""

	def __init__(self, value, row=None, header=None, **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		self.value = value

		self.row = row
		self.header = header

		self.type = str
		self.align = None
		self.format = "%s"
		self.cls = None
		self.style = None

		if self.header:
			self.type = self.header.type
			self.align = self.header.align
			self.format = self.header.format
			self.cls = self.header.ccls
			self.style = self.header.cstyle

		self.type = kwargs.get("type", self.type)
		self.align = kwargs.get("align", self.align)
		self.format = kwargs.get("format", self.format)
		self.cls = kwargs.get("cls", self.cls)
		self.style = kwargs.get("style", self.style)

	def _format(self):
		if type(self.format) == types.FunctionType:
			return self.format(self.value)
		else:
			return self.format % self.value

	def __str__(self):
		if self.header is not None and self.align:
			width = self.header.width
			if self.align == "left":
				return self.format().ljust(widtH)
			elif self.align == "center":
				return self.format().center(widtH)
			elif self.align == "right":
				return self.format().rjust(widtH)
			else:
				return self.format().ljust(width)
		else:
			return self._format()
	
	def toHTML(self):
		align, cls, style = ("",) * 3
		if self.align:
			align = "align=\"%s\"" % self.align
		if self.cls:
			cls = "class=\"%s\"" % self.cls
		if self.style:
			style = "style=\"%s\"" % self.style
		attrs = " ".join([align, cls, style]).strip()
		if attrs == "":
			return "<td>%s</td>" % self._format()
		else:
			return "<td %s>%s</td>" % (attrs, self._format())

class Table(object):
	"""Table(rows=[], headers=[], **kwargs) -> new table object

	Container class to hold a set of rows and headers
	allowing easy traversal and display.

	If the optional rows or headers argumnets are given,
	these are used as the table row data and headers.

	An Optional list of kwargs can also be supplied that
	affect how this table is created:
	 * cls   - class attribute used by toHTML
	 * style - style attribute used by toHTML

	Example
	-------
	>>> c = Cell(22.0/7.0, format="%0.2f", align="right", cls="foo", style="hidden: true")
	>>> r = Row([c], cls="asdf", style="qwerty")
	>>> h = Header("Test")
	>>> t = Table([r], [h])
	>>> print t
	Test
	----
	3.14
	----

	>>> print t.toHTML()
	<table><th>Test</th><tr class="asdf" style="qwerty"><td align="right" class="foo" style="hidden: true">3.14</td></td></table>
	>>>
	"""

	def __init__(self, rows=[], headers=[], **kwargs):
		"initializes x; see x.__class__.__doc__ for signature"

		self.rows = rows
		self.headers = headers

		self.cls = kwargs.get("cls", None)
		self.style = kwargs.get("style", None)

	def __str__(self):
		s = StringIO()
		s.write("".join([str(header) for header in self.headers]))
		s.write("\n")
		s.write("-" * sum([header.width for header in self.headers]))
		s.write("\n")
		for row in self.rows:
			s.write("%s\n" % str(row))
		s.write("-" * sum([header.width for header in self.headers]))
		s.write("\n")
		v = s.getvalue()
		s.close()
		return v

	def toHTML(self):
		cls, style = ("",) * 2
		if self.cls:
			cls = "class=\"%s\"" % self.cls
		if self.style:
			style = "style=\"%s\"" % self.style
		attrs = " ".join([cls, style]).strip()

		s = StringIO()
		if attrs == "":
			s.write("<table>")
		else:
			s.write("<table %s>" % attrs)	
		s.write("".join([header.toHTML() for header in self.headers]))
		s.write("".join([row.toHTML() for row in self.rows]))
		s.write("</table>")
		v = s.getvalue()
		s.close()
		return v

	def getXY(self, x, y):
		return self.rows[y].getCell(x)