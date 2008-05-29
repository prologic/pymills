#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from pymills.wsgi import WSGIServer

def app(environ, start_response):
	status = "200 OK"
	response_headers = [("Content-type", "text/plain")]
	start_response(status, response_headers)
	return ["Hello world!"]

def main():
	server = WSGIServer(
			("0.0.0.0", 8000), app,
			server_name="www.example.com")

	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()

if __name__ == "__main__":
	main()
