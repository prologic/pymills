# Filename:	spider.py
# Module:	spider
# Date:		19th September 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $LastChangedDate: 2005-09-13 01:18:53 +1000 (Tue, 13 Sep 2005) $
# $Author: prologic $
# $Id: __init__.py 81 2005-09-12 15:18:53Z prologic $

"""Web Crawler Module

This is a module which implements a web crawler.
"""

import sys
import string
import urllib2
import urlparse
from BeautifulSoup import BeautifulSoup

try:
	import psyco
	from psyco.classes import *
	psyco.full()
except ImportError:
	pass

class Node:

	def __init__(self, host, url):
		self._url = url
		self._host = host
		self._children = []
	
	def add(self, node):
		self._children.append(node)

class Crawler:

	def __init__(self, url, depth, lock=True):
		self._url = url
		self._depth = depth
		self._lock = lock
		self._host = urlparse.urlparse(url)[1]
	
	def crawl(self):
		pass

class Fetcher:

	def __init__(self, url):
		self._url = url
		self._root = self._url
		self._tags = []
		self._urls = []
	
	def __getitem__(self, y):
		return self._urls[y]

	def open(self):
		url = self._url
		try:
			handle = urllib2.urlopen(url)
		except IOError:
			return None
		return handle

	def fetch(self):
		host = urlparse.urlparse(self._url)[1]
		handle = self.open()
		soup = BeautifulSoup()
		soup.feed(handle.read())
		tags = soup('a')
		for tag in tags:
			try:
				url = urlparse.urljoin(self._url, tag['href'])
			except KeyError:
				continue
			self._urls.append(url)
	
def test():
	url = sys.argv[1]
	page = Fetcher(url)
	page.fetch()
	for i, url in enumerate(page):
		print "%d. %s" % (i, url)

if __name__ == "__main__":
	test()
