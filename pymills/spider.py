# Filename:	spider.py
# Module:	spider
# Date:		19th September 2005
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Web Crawler/Spider

This module implements a web crawler. This is very _basic_ only
and needs to be extended to do anything usefull with the
traversed pages.
"""

import re
import sys
import time
import urllib2
import urlparse
import collections
from BeautifulSoup import BeautifulSoup, Null

try:
	import psyco
	psyco.full()
except ImportError:
	pass

import spider
import pymills.url
from pymills.misc import duration

AGENT = "%s-%s/%s" % (pymills.__name__, spider.__name__, pymills.__version__)

### The Main Classes

class Crawler:

	def __init__(self, root, maxLinks, lock=True):
		self._root = root
		self._maxLinks = maxLinks
		self._lock = lock
		self._host = urlparse.urlparse(root)[1]
		self._startTime = 0
		self._countLinks = 0
		self._countFollowed = 0
	
	def getStats(self):
		return (self._startTime, self._countLinks, self._countFollowed)

	def crawl(self):

		self._startTime = time.time()

		page = Fetcher(self._root)
		page.fetch()
		urls = collections.deque(page.getURLS())
		followed = [self._root]

		n = 0
		done = False

		while not done:
			n += 1
			url = urls.popleft()
			if url not in followed:
				host = urlparse.urlparse(url)[1]
				if self._lock and re.match(".*%s" % self._host, host):
					followed.append(url)
					self._countFollowed += 1
					print "Following: %s" % url
					page = Fetcher(url)
					page.fetch()
					for i, url in enumerate(page):
						if not url in urls:
							self._countLinks += 1
							urls.append(url)
							print "New: %s" % url
					if n > self._maxLinks and self._maxLinks > 0:
						done = True

class Fetcher:

	def __init__(self, url):
		self._url = url
		self._root = self._url
		self._tags = []
		self._urls = []
	
	def __getitem__(self, y):
		return self._urls[y]

	def _add_headers(self, request):
		request.add_header("User-Agent", AGENT)

	def getURLS(self):
		return self._urls

	def open(self):
		url = self._url
		try:
			request = urllib2.Request(url)
			handle = urllib2.build_opener()
		except IOError:
			return None
		return (request, handle)

	def fetch(self):
		(request, handle) = self.open()
		self._add_headers(request)
		if handle is not None:
			soup = BeautifulSoup()
			try:
				content = handle.open(request).read()
				soup.feed(content)
				title = soup.html.head.title.string
				if title == Null:
					title = ""
				tags = soup('a')
			except urllib2.HTTPError, error:
				if error.code == 404:
					print "%s -> %s" % (error, error.url)
				else:
					print error
				tags = []
			except urllib2.URLError, error:
				print error
				tags = []
			for tag in tags:
				try:
					url = urlparse.urljoin(self._url, pymills.url.unescape(tag['href']))
				except KeyError:
					continue
				self._urls.append(url)
	
### Test Functions

def testFetcher():
	url = sys.argv[1]
	page = Fetcher(url)
	page.fetch()
	for i, url in enumerate(page):
		print "%d. %s" % (i, url)

def testCrawler():
	url = sys.argv[1]
	maxLinks = int(sys.argv[2])
	crawler = Crawler(url, maxLinks)
	crawler.crawl()
	print "DONE"
	startTime, countLinks, countFollowed = crawler.getStats()
	print "Found %d links, following %d urls in %s+%s:%s:%s" % ((countLinks, countFollowed,) + duration(time.time() - startTime))

### Main

if __name__ == "__main__":
	testCrawler()
