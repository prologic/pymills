# Filename: config.py
# Module:	config
# Date:		11th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Config

This is a small layer on-top of the standard-library's
ConfiguParser for ini-style configuration files.
It simply just provides some nice convenient access methods.
"""

from ConfigParser import ConfigParser

TRUE_VALUES = ("yes", "true", "on", "aye", "1", 1, True)

class Configuration:
	"""Configuration(filename) -> new configuration object
	
	Thin layer over ConfigParser from the Python standard
	library. Just provides some convenience methods.
	"""

	def __init__(self, filename):
		"Creates x; see x.__class__.__doc__ for signature"

		self._defaults = {}
		self.filename = filename
		self.parser = ConfigParser()
		self.parser.read(self.filename)

	def __contains__(self, name):
		"x.__getitem__(y) <==> x[y]"

		return self.parser.has_section(name)

	def get(self, section, name, default=None):
		"""C.get(section, name, default=None) -> str
		
		Return the specified option.

		If the specified option doesn't exist, the default
		is returned.
		"""

		if not self.parser.has_option(section, name):
			return self._defaults.get((section, name)) or default or ''
		return self.parser.get(section, name)

	def getint(self, section, name, default=None):
		"""C.getint(section, name, default=None) -> int

		Return the specified option as an int value.

		If the specified option doesn't exist, the default
		is returned.
		"""

		try:
			return int(self.get(section, name, default))
		except ValueError:
			return default

	def getbool(self, section, name, default=None):
		"""C.getbool(section, name, default=None) -> bool
		
		Return the specified option as a bool value.

		If the specified option doesn't exist, the default
		is returned. If the value of the option is one of
		"yes", "true", "on" or "1", this will return True,
		otherwise False.
		"""

		if isinstance(default, basestring):
			default = default.lower()
		return self.get(section, name, default) in TRUE_VALUES

	def setdefault(self, section, name, value):
		"""C.setdefault(section, name, value) -> None
		
		Set the default value for the specified option.
		"""

		if (section, name) not in self._defaults:
			self._defaults[(section, name)] = value

	def set(self, section, name, value):
		"""C.set(section, name, value) -> None
		
		Set the specified option to the value spcified.
		If no section exists for the spcified option, one
		will be created. These changes are not persistent
		unless saved with	C.save()
		"""

		if not self.parser.has_section(section):
			self.parser.add_section(section)
		self.parser.set(section, name, value)

	def options(self, section):
		"""C.options(section) -> list of options or []

		Returns a list of options for the specified section.
		If there are no options for the given section, an
		empty list is returned.
		"""

		options = []
		if self.parser.has_section(section):
			for option in self.parser.options(section):
				options.append((option, self.parser.get(section, option)))
		for option, value in self._defaults.iteritems():
			if option[0] == section:
				if not [exists for exists in options if exists[0] == option[1]]:
					options.append((option[1], value))
		return options

	def remove(self, section, name):
		"""C.remove(section, name) -> None

		Remove the specified option if it exists.
		"""

		if self.parser.has_section(section):
			self.parser.remove_option(section, name)

	def sections(self):
		"C.section() -> dict of sections"

		return self.parser.sections()

	def save(self):
		"""C.save() -> None

		Save the configuration object to disk. Thils will
		overwrite the file given by self.filename.
		"""

		if not self.filename:
			return
		fileobj = file(self.filename, 'w')
		try:
			self.parser.write(fileobj)
		finally:
			fileobj.close()
