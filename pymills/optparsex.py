# Filename: optparsex.py
# Module:	optparsex
# Date:		14th Oct 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Option Parser Extended

This module extends python's standard optarse module.
"""

import optparse
from optparse import _match_abbrev

from adt import CaselessDict

class CaselessOptionParser(optparse.OptionParser):

	def _create_option_list(self):
		self.option_list = []
		self._short_opt = CaselessDict()
		self._long_opt = CaselessDict()
		self._long_opts = []
		self.defaults = {}

	def _match_long_opt(self, opt):
		return _match_abbrev(opt.lower(), self._long_opt.keys())

class Option(optparse.Option):

	ATTRS = optparse.Option.ATTRS + ['required']

	def _check_required(self):
		if self.required and not self.takes_value():
			raise optparse.OptionError(
				"required flag set for option that doesn't take a value",
				self)

	# Make sure _check_required() is called from the constructor!
	CHECK_METHODS = optparse.Option.CHECK_METHODS + [_check_required]

	def process(self, opt, value, values, parser):
		optparse.Option.process(self, opt, value, values, parser)
		parser.option_seen[self] = 1

class OptionParser(optparse.OptionParser):

	def _init_parsing_state(self):
		optparse.OptionParser._init_parsing_state(self)
		self.option_seen = {}

	def check_values(self, values, args):
		for option in self.option_list:
			if (isinstance(option, Option) and
					option.required and
					not self.option_seen.has_key(option)):
				self.error("%s not supplied" % option)
		return (values, args)