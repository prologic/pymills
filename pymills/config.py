# Filename: config.py
# Module:	config
# Date:		11th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: __init__.py 202 2006-05-26 18:58:45Z prologic $

"""Config

...
"""

import os
import sys
from ConfigParser import ConfigParser

TRUE_VALUES = ("yes", "true", "on", "aye", "1", 1, True)

class Configuration:
	"""Thin layer over `ConfigParser` from the Python standard library.

	In addition to providing some convenience methods, the class remembers
	the last modification time of the configuration file, and reparses it
	when the file has changed.
	"""

	def __init__(self, filename):
		self._defaults = {}
		self.filename = filename
		self.parser = ConfigParser()
		self.parser.read(self.filename)

	def __contains__(self, name):
		return self.parser.has_section(name)

	def get(self, section, name, default=None):
		if not self.parser.has_option(section, name):
			return self._defaults.get((section, name)) or default or ''
		return self.parser.get(section, name)

	def getint(self, section, name, default=None):
		try:
			return int(self.get(section, name, default))
		except ValueError:
			return default

	def getbool(self, section, name, default=None):
		"""Return the specified option as boolean value.
		
		If the value of the option is one of "yes", "true", "on", or "1", this
		method wll return `True`, otherwise `False`.
		
		(since Trac 0.9.3)
		"""
		if isinstance(default, basestring):
			default = default.lower()
		return self.get(section, name, default) in TRUE_VALUES

	def setdefault(self, section, name, value):
		if (section, name) not in self._defaults:
			self._defaults[(section, name)] = value

	def set(self, section, name, value):
		"""Change a configuration value.
		
		These changes are not persistent unless saved with `save()`.
		"""
		if not self.parser.has_section(section):
			self.parser.add_section(section)
		return self.parser.set(section, name, value)

	def options(self, section):
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
		if self.parser.has_section(section):
			self.parser.remove_option(section, name)

	def sections(self):
		return self.parser.sections()

	def save(self):
		if not self.filename:
			return
		fileobj = file(self.filename, 'w')
		try:
			self.parser.write(fileobj)
		finally:
			fileobj.close()
