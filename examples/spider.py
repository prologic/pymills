#!/usr/bin/env python

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
import optparse
import collections
from BeautifulSoup import BeautifulSoup

try:
	import psyco
	psyco.full()
except ImportError:
	pass

import spider
import pymills
from pymills.web import escape
from pymills.misc import duration
from pymills import __version__ as systemVersion

USAGE = "%prog [options] <url>"
VERSION = "%prog v" + systemVersion

AGENT = "%s-%s/%s" % (pymills.__name__, spider.__name__, pymills.__version__)

class Crawler(object):

	def __init__(self, root, depth, lock=True):
		self._root = root
		self._depth = depth
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
						if url not in urls:
							self._countLinks += 1
							urls.append(url)
							print "New: %s" % url
					if n > self._depth and self._depth > 0:
						done = True

class Fetcher(object):

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
				if soup.html is not None:
					title = soup.html.head.title.string
				else:
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
					url = urlparse.urljoin(self._url, escape(tag['href']))
				except KeyError:
					continue
				self._urls.append(url)

def getLinks(url):
	page = Fetcher(url)
	page.fetch()
	for i, url in enumerate(page):
		print "%d. %s" % (i, url)

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-q", "--quiet",
			action="store_true", default=False, dest="quiet",
			help="Enable quiet mode")

	parser.add_option("-l", "--links",
			action="store_true", default=False, dest="links",
			help="Get links for specified url only")

	parser.add_option("-d", "--depth",
			action="store", default=30, dest="depth",
			help="Maximum depth to traverse")

	opts, args = parser.parse_args()

	if len(args) < 1:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

def main():
	opts, args = parse_options()

	url = args[0]

	if opts.links:
		getLinks(url)
		raise SystemExit, 0

	depth = int(opts.depth)
	print >> sys.stderr, "Crawling %s (Max Depth: %d)" % (
			url, depth)
	crawler = Crawler(url, depth)
	crawler.crawl()
	print >> sys.stderr, "DONE"
	startTime, countLinks, countFollowed = crawler.getStats()
	print >> sys.stderr, "Found %d links, following %d urls in %s+%s:%s:%s" % (
			(countLinks, countFollowed,) + duration(time.time() - startTime))

if __name__ == "__main__":
	main()
