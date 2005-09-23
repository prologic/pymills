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
import collections
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

	def __init__(self, root, urls, maxLinks, lock=True):
		self._root = root
		self._urls = urls
		self._maxLinks = maxLinks
		self._lock = lock
		self._host = urlparse.urlparse(root)[1]
	
	def crawl(self):

		urls = collections.deque(self._urls[:])
		n = 0
		done = False

		while not done:
			n += 1
			url = urls.popleft()
			print "Following: %s" % url
			page = Fetcher(url)
			page.fetch()
			for i, url in enumerate(page):
				if not url in urls:
					urls.append(url)
					print "New: %s" % url
			if n > self._maxLinks:
				done = True

class Fetcher:

	def __init__(self, url):
		self._url = url
		self._root = self._url
		self._tags = []
		self._urls = []
	
	def __getitem__(self, y):
		return self._urls[y]

	def getURLS(self):
		return self._urls

	def open(self):
		url = self._url
		try:
			handle = urllib2.urlopen(url)
		except IOError:
			return None
		return handle

	def fetch(self):
		handle = self.open()
		if handle is not None:
			soup = BeautifulSoup()
			soup.feed(handle.read())
			tags = soup('a')
			for tag in tags:
				try:
					url = urlparse.urljoin(self._url, tag['href'])
				except KeyError:
					continue
				self._urls.append(url)
	
def testFetcher():
	url = sys.argv[1]
	page = Fetcher(url)
	page.fetch()
	for i, url in enumerate(page):
		print "%d. %s" % (i, url)

def testCrawler():
	url = sys.argv[1]
	maxLinks = int(sys.argv[2])
	page = Fetcher(url)
	page.fetch()
	crawler = Crawler(url, page.getURLS(), maxLinks)
	crawler.crawl()

if __name__ == "__main__":
	testCrawler()
