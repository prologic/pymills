# Module:   table
# Date:     17th December 2007
# Author:   James Mills, James dot Mills at au dot pwc dot com

"""Table generation, display and manipulation module.

Classes to generate ASCII and HTML tables and traverse
data.
"""


from StringIO import StringIO


class Header(object):
    """Create a new Header

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

    Example::

        >>> h = Header("Test")
        >>> print h
        Test
        >>> print h.toHTML()
        <th>Test</th>
        >>>
    """

    def __init__(self, name, table=None, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        self.name = name
        self.table = table

        self.type = kwargs.get("type", str)
        self.align = kwargs.get("align", None)
        self.hidden = kwargs.get("hidden", False)
        self.format = kwargs.get("format", "%s")
        self.width = kwargs.get("width", self.getWidth())
        self.cls = kwargs.get("cls", None)
        self.style = kwargs.get("style", None)
        self.ccls = kwargs.get("ccls", None)
        self.cstyle = kwargs.get("cstyle", None)

    def refresh(self):
        self.width = self.getWidth()

    def getWidth(self):
        if self.hidden:
            return 0
        if self.table:
            rows = self.table.rows
            hIndex = self.table.headers.index(self)
            return max(
                max([len(str(x[hIndex])) for x in rows]) + 2,
                len(self.name) + 2)
        else:
            return len(self.name)

    def __str__(self):
        if self.hidden:
            return ""

        width = self.width
        if self.align == "left":
            return self.name.ljust(width)
        elif self.align == "center":
            return self.name.center(width)
        elif self.align == "right":
            return self.name.rjust(width)
        else:
            return self.name.ljust(width)

    def toHTML(self):
        if self.hidden:
            return ""

        align, cls, style = (None,) * 3
        if self.align:
            align = "align=\"%s\"" % self.align
        if self.cls:
            cls = "class=\"%s\"" % self.cls
        if self.style:
            style = "style=\"%s\"" % self.style
        attrs = " ".join(x for x in [align, cls, style] if x is not None).strip()
        if attrs == "":
            return " <th>%s</th>" % self.name
        else:
            return " <th %s>%s</th>" % (attrs, self.name)


class Row(list):
    """Create a new Row

    Container class that holds the definition of a table
    row and a set of cells and how each cell should be
    formatted and displayed.

    An Optional list of kwargs can also be supplied that
    affect how this row is created:

    * hidden - whether this row is displayed.
    * cls    - class attribute used by toHTML
    * style  - style attribute used by toHTML

    Example::

        >>> c = Cell(22.0/7.0, format="%0.2f", align="right", cls="foo", style="hidden: true")
        >>> r = Row([c], cls="asdf", style="qwerty")
        >>> print r
        3.14
        >>> print r.toHTML()
        <tr class="asdf" style="qwerty"><td align="right" class="foo" style="hidden: true">3.14</td></td>
        >>>
    """

    def __init__(self, cells, table=None, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Row, self).__init__(cells)

        self.cells = self
        self.table = table

        self.hidden = kwargs.get("hidden", False)
        self.cls = kwargs.get("cls", None)
        self.style = kwargs.get("style", None)

    def refresh(self):
        for i, cell in enumerate(self.cells):
            cell.row = self
            cell.table = self.table
            cell.header = self.table.headers[i]
            cell.refresh()

    def __str__(self):
        if self.hidden:
            return ""
        else:
            return "".join([str(cell) for cell in self.cells])

    def toHTML(self):
        if self.hidden:
            return "\n"
        else:
            cls, style = (None,) * 2
            if self.cls:
                cls = "class=\"%s\"" % self.cls
            if self.style:
                style = "style=\"%s\"" % self.style
            attrs = " ".join(x for x in [cls, style] if x is not None).strip()

            cells = "\n  ".join([cell.toHTML() for cell in self.cells])
            if attrs == "":
                return " <tr>\n  %s\n </tr>" % cells
            else:
                return " <tr %s>\n  %s\n </tr>" % (attrs, cells)


class Cell(object):
    """Create a new Cell

    Container class that holds the definition of a table
    cell and it's value and how it should be formatted
    and displayed.

    An Optional list of kwargs can also be supplied that
    affect how this header is created:

    * type   - the data type. Must be compatible with type(x)
    * align  - text alignment. one of "left", "center", or "right"
    * hidden - whether this cell is displayed
    * format - format str or callable
    * cls    - class attribute used by toHTML
    * style  - style attribute used by toHTML

    Example::

        >>> c = Cell(22.0/7.0, format="%0.2f", align="right", cls="foo", style="hidden: true")
        >>> print c
        3.14
        >>> print c.toHTML()
        <td align="right" class="foo" style="hidden: true">3.14</td>
        >>>
    """

    def __init__(self, value, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        self.value = value

        self.row = None
        self.header = None

        self.type = kwargs.get("type", type(self.value))
        self.align = kwargs.get("align", None)
        self.hidden = kwargs.get("hidden", False)
        self.format = kwargs.get("format", None)
        if self.format is None:
            if self.type == float:
                self.format = "%0.2f"
            elif self.type == int:
                self.format = "%d"
            else:
                self.format = "%s"
        self.cls = kwargs.get("cls", None)
        self.style = kwargs.get("style", None)

    def refresh(self):
        if self.header:
            self.type = self.header.type or self.type
            self.align = self.header.align or self.align
            self.hidden = self.header.hidden or self.hidden
            self.format = self.header.format or self.format
            self.cls = self.header.ccls or self.cls
            self.style = self.header.cstyle or self.style

    def _format(self):
        if callable(self.format):
            return self.format(self.value)
        else:
            return self.format % self.value

    def __str__(self):
        if self.hidden:
            return ""

        if self.header:
            width = self.header.width
            if self.align == "left":
                return self._format().ljust(width)
            elif self.align == "center":
                return self._format().center(width)
            elif self.align == "right":
                return self._format().rjust(width)
            else:
                return self._format().ljust(width)
        else:
            return self._format()

    def toHTML(self):
        if self.hidden:
            return ""

        align, cls, style = (None,) * 3
        if self.align:
            align = "align=\"%s\"" % self.align
        if self.cls:
            cls = "class=\"%s\"" % self.cls
        if self.style:
            style = "style=\"%s\"" % self.style
        attrs = " ".join(x for x in [align, cls, style] if x is not None).strip()
        if attrs == "":
            return "<td>%s</td>" % self._format()
        else:
            return "<td %s>%s</td>" % (attrs, self._format())

    def getHeader(self):
        return self.row.table.headers[self.row.table.rows[0].index(self)]


class Table(list):
    """Create a new Table

    Container class to hold a set of rows and headers
    allowing easy traversal and display.

    An Optional list of kwargs can also be supplied that
    affect how this table is created:

    * cls   - class attribute used by toHTML
    * style - style attribute used by toHTML

    Example::

        >>> c = Cell(22.0/7.0, format="%0.2f", align="right", cls="foo", style="hidden: true")
        >>> r = Row([c], cls="asdf", style="qwerty")
        >>> h = Header("Test")
        >>> t = Table([h], [r])
        >>> print t
        Test
        ----
        3.14
        ----

        >>> print t.toHTML()
        <table><th>Test</th><tr class="asdf" style="qwerty"><td align="right" class="foo" style="hidden: true">3.14</td></td></table>
        >>>
    """

    def __init__(self, headers, rows=[], **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Table, self).__init__(rows)

        self.headers = headers
        self.rows = self

        self.cls = kwargs.get("cls", None)
        self.style = kwargs.get("style", None)

    def append(self, row):
        row.table = self
        row.refresh()
        super(Table, self).append(row)

    def refresh(self):
        for header in self.headers:
            header.table = self
        for row in self.rows:
            row.table = self

        for header in self.headers:
            header.refresh()

        for row in self.rows:
            row.refresh()

    def __repr__(self):
        return "<Table %s rows=%d>" % (id(self), len(self.rows))

    def __str__(self):
        s = StringIO()

        separator = "-" * sum([header.width for header in self.headers])

        s.write("".join([str(header) for header in self.headers]))
        s.write("\n%s\n" % separator)
        s.write("\n".join([str(row) for row in self.rows]))
        s.write("\n%s\n" % separator)

        v = s.getvalue()
        s.close()

        return v

    def toHTML(self):
        cls, style = (None,) * 2
        if self.cls:
            cls = "class=\"%s\"" % self.cls
        if self.style:
            style = "style=\"%s\"" % self.style
        attrs = " ".join(x for x in [cls, style] if x is not None).strip()

        s = StringIO()
        if attrs == "":
            s.write("<table>\n")
        else:
            s.write("<table %s>\n" % attrs)
        s.write("\n".join([header.toHTML() for header in self.headers]))
        s.write("\n")
        s.write("\n".join([row.toHTML() for row in self.rows]))
        s.write("\n")
        s.write("</table>")
        v = s.getvalue()
        s.close()
        return v

    def getXY(self, x, y):
        return self.rows[y].getCell(x)


def test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    test()
