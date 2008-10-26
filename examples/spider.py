#!/usr/bin/env python

"""Web Crawler/Spider

This module implements a web crawler. This is very _basic_ only
and needs to be extended to do anything usefull with the
traversed pages.
"""

import re
import sys
import time
import math
import urllib2
import urlparse
import optparse
from BeautifulSoup import BeautifulSoup

import pymills
from pymills.utils import encodeHTML
from pymills.datatypes import Queue
from pymills import __version__ as systemVersion

USAGE = "%prog [options] <url>"
VERSION = "%prog v" + systemVersion

AGENT = "%s/%s" % (pymills.__name__, pymills.__version__)

class Crawler(object):

	def __init__(self, root, depth, locked=True):
		self.root = root
		self.depth = depth
		self.locked = locked
		self.host = urlparse.urlparse(root)[1]
		self.links = 0
		self.followed = 0

	def crawl(self):
		page = Fetcher(self.root)
		page.fetch()
		urls = Queue()
		for url in page.urls:
			urls.push(url)
		followed = [self.root]

		n = 0

		while not urls.empty():
			n += 1
			url = urls.pop()
			if url not in followed:
				try:
					host = urlparse.urlparse(url)[1]
					if self.locked and re.match(".*%s" % self.host, host):
						followed.append(url)
						self.followed += 1
						page = Fetcher(url)
						page.fetch()
						for i, url in enumerate(page):
							if url not in urls:
								self.links += 1
								urls.push(url)
						if n > self.depth and self.depth > 0:
							break
				except Exception, error:
					print "Warning: Can't process url '%s'" % url

class Fetcher(object):

	def __init__(self, url):
		self.url = url
		self.urls = []

	def __contains__(self, x):
		return x in self.urls

	def __getitem__(self, x):
		return self.urls[x]

	def _addHeaders(self, request):
		request.add_header("User-Agent", AGENT)

	def open(self):
		url = self.url
		print "Following %s" % url
		try:
			request = urllib2.Request(url)
			handle = urllib2.build_opener()
		except IOError:
			return None
		return (request, handle)

	def fetch(self):
		request, handle = self.open()
		self._addHeaders(request)
		if handle:
			soup = BeautifulSoup()
			try:
				content = unicode(handle.open(request).read(), errors="ignore")
				soup.feed(content)
				tags = soup('a')
			except urllib2.HTTPError, error:
				if error.code == 404:
					print >> sys.stderr, "ERROR: %s -> %s" % (error, error.url)
				else:
					print >> sys.stderr, "ERROR: %s" % error
				tags = []
			except urllib2.URLError, error:
				print >> sys.stderr, "ERROR: %s" % error
				tags = []
			for tag in tags:
				try:
					href = tag["href"]
					if href is not None:
						url = urlparse.urljoin(self.url, encodeHTML(href))
						if url not in self:
							print " Found: %s" % url
							self.urls.append(url)
				except KeyError:
					pass

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
			action="store", type="int", default=30, dest="depth",
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

	depth = opts.depth

	sTime = time.time()

	print "Crawling %s (Max Depth: %d)" % (url, depth)
	crawler = Crawler(url, depth)
	crawler.crawl()

	eTime = time.time()
	tTime = eTime - sTime

	print "Found:    %d" % crawler.links
	print "Followed: %d" % crawler.followed
	print "Stats:    (%d/s after %0.2fs)" % (
			int(math.ceil(float(crawler.links) / tTime)), tTime)

if __name__ == "__main__":
	main()
