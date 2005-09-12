# Filename: ports.py
# Module:	ports
# Date:		15th June 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate$
# $Author$
# $Id$

"""Ports System module

Create an internal representation of the system's Ports Tree
"""

import re
import os
import StringIO

from pymills import utils

FILEFORMAT = \
"""# $Id$
# Description: %(Description)s
# URL:         %(URL)s
# Packager:    %(Packager)s
# Maintainer:  %(Maintainer)s
#
# Depends on: %(depsStr)s

name=%(name)s
version=%(version)s
release=%(release)s
source=(%(sourcesStr)s)

build () {
%(buildStr)s
}

# vim: syntax=sh\n"""

STRFORMAT = \
"""Name:         %(name)s
Path:         %(path)s
Version:      %(version)s
Release:      %(release)s
Description:  %(Description)s
URL:          %(URL)s
Packager:     %(Packager)s
Maintainer:   %(Maintainer)s
Dependencies: %(depsStr)s\n"""

RULES = [
	(0, " *# *Description: *(.*?)\n", "Description"),
	(1, " *# *URL: *(.*?)\n", "URL"),
	(2, " *# *Packager: *(.*?)\n", "Packager"),
	(3, " *# *Maintainer: *(.*?)\n", "Maintainer"),
	(4, " *# *Depends on: *(.*?)\n", "deps"),
	(5, "name=(.*?)\n", "name"),
	(5, "version=(.*?)\n", "version"),
	(6, "release=(.*?)\n", "release"),
	(7, "source=\((.*?)\)\n", "sources"),
	(8, "build *\( *\) *{\n(.*)\n}", "build")]

class Error(Exception):
	pass

class PortsTree:
	
	def __init__(self, path):
		
		self._path = path
		self._repos = []
		
	def __str__(self):
		f = StringIO.StringIO()
		f.write("Ports Tree: %s\n" % self._path)
		f.write("-----------\n\n")
		f.writelines(self._repos)
		f.write("Total ports: %d" % len(self._repos))
		output = f.getvalue()
		f.close()
		return output

	def buildTree(self):
		dirs = utils.getFiles(self._path, [os.path.isdir], "^[^.].*")
		
		for dir in dirs:
			repo = Repository(self._path, dir)
			repo.buildList()
				
			if not repo == []:
				self._repos.append(repo)

class Repository:

	def __init__(self, root, name):
		
		self._root = root
		self._name = name
		self._ports = []
		
	def __str__(self):
		f = StringIO.StringIO()
		f.write("%s:\n" % self._name)
		f.writelines(self._ports)
		f.write("\n")
		output = f.getvalue()
		f.close()
		return output

	def buildList(self):
		path = os.path.join(self._root, self._name)
		dirs = utils.getFiles(path, [os.path.isdir], "^[^.].*")
		
		for dir in dirs:
			port = Port(path, dir)
			self._ports.append(port)

class Port:

	def __init__(self, root, name):
		self._root= root
		self._name = name
	
	def __str__(self):
		return "   %s\n" % self._name

class Pkgfile:

	def __init__(self, file):

		self.__dict = {
			"Description": "",
			"URL": "",
			"Packager": "",
			"Maintainer": "",
			"deps": [],
			"depsStr": "",

			"path": os.path.dirname(file) or "./",
			"name": "",
			"version": "",
			"release": "",
			"sources": [],
			"sourcesStr": "",
			"build": [],
			"buildStr": ""
		}


		self.__parse(file)
	
	def __repr__(self):
		return STRFORMAT % self.__dict

	def __getitem__(self, key):
		return self.__dict[key]

	def __parse(self, file):

		fd = open(file, "r")
		input = fd.read()
		fd.close()

		for i, match, key in RULES:
			m = re.search(match, input, \
					re.IGNORECASE + \
					re.DOTALL)
			if m is not None:
				if i == 4:
					self.__dict[key] = [x.strip() for x in m.group(1).split(",")]
					self.__dict["%sStr" % key] = m.group(1)
				elif i == 7:
					self.__dict[key] = [x.strip() for x in m.group(1).split(" ")]
					self.__dict["%sStr" % key] = m.group(1)
				elif i == 8:
					self.__dict[key] = [x.strip() for x in m.group(1).split("\n")]
					self.__dict["%sStr" % key] = m.group(1)
				else:
					self.__dict[key] = m.group(1).strip()
	
	def writeTo(self, file):
		fd = open(file, "w")
		fd.write(FILEFORMAT % self.__dict)
		fd.close()
	
if __name__ == "__main__":
	portsTree = PortsTree("/usr/ports")
	portsTree.buildTree()
	print portsTree
