# Filename: crux.py
# Module:   crux
# Date:     07th June 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""CRUX Module"""

import os
import re
import urllib
import urlparse

import ver

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
	
	def getDescription(self):
		return self.__dict["Description"]

	def getURL(self):
		return self.__dict["URL"]
	
	def getPackager(self):
		return self.__dict["Packager"]
	
	def getMaintainer(self):
		return self.__dict["Maintainer"]
	
	def getDeps(self):
		return self.__dict["deps"]
	
	def getName(self):
		return self.__dict["name"]

	def setVersion(self, version):
		self.__dict["version"] = version

	def getVersion(self):
		return self.__dict["version"]

	def getRelease(self):
		return self.__dict["release"]

	def getSources(self):
		return self.__dict["sources"]

	def getBuild(self):
		return self.__dict["build"]

	def substVars(self, s):

		s = re.sub("\$\{?name\}?", self.getName(), s)
		s = re.sub("\$\{?version\}?", self.getVersion(), s)

		return s

	def fileToRE(self, file):

		#print "file: %s" % file
		s = file

		s = s.replace(self.getName(), "%s")
		s = s.replace(self.getVersion(), "%s")
		s = s.replace(".", "\.")

		#print "s = %s" % s

		extra = re.sub("[0-9]", "", self.getVersion())

		#print "extra = %s" % extra

		try:
			reExp = s % (self.getName(), "[0-9%s]+" % extra)
		except:
			reExp = s % ("[0-9%s]+" % extra)

		try:
			verExp = s % (self.getName(), "([0-9%s]+)" % extra)
		except:
			verExp = s % ("([0-9%s]+)" % extra)

		#print "reExp = %s" % reExp
		#print "verExp = %s" % verExp

		return (reExp, verExp, extra)

	def getLatestVersion(self):

		name = self.getName()
		version = self.getVersion()

		sources = self.getSources()

		url = None

		for source in sources:
			source = self.substVars(source)
			scheme, netloc, path, params, query, fragment = \
					urlparse.urlparse(source)
			if not scheme == "":
				file = os.path.basename(path)
				path = os.path.dirname(path)
				url = urlparse.urlunparse((scheme, netloc, path, params, query, fragment))
				break

		if url is None:
			return self.getVersion()

		#print "URL: %s" % url

		try:
			fd = urllib.urlopen(url)
			page = fd.read()
			fd.close()
		except Exception, e:
			print "%s: error, error fetching url (%s)" % (self.getName(), e)
			return self.getVersion()

		(reExp, verExp, extra) = self.fileToRE(file)

		curVer = ver.Version(self.getVersion())
		#print curVer
		newVer = self.getVersion()
		matches = re.findall(reExp, page)
		if matches == []:
			print "%s: error, empty result set" % self.getName()
		for match in matches:
			m = re.search(verExp, match)
			verStr = m.group(1)
			tmpVer = ver.Version(verStr)
			if tmpVer > curVer:
				newVer = verStr

		return newVer
