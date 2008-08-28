#!/usr/bin/env python

import cherrypy
from cherrypy import expose

class Root:

	@expose
	def index(self):
		return ""

	@expose
	def test(self):
		return "OK"

	@expose
	def hello(self):
		if cherrypy.request.cookie.get("seen", False):
			return "Seen you before!"
		else:
			cherrypy.response.cookie["seen"] = True
			return "Hello World!"

def main():
	config = {"global": {
		"server.socket_port": 8000,
		"server.socket_host": "0.0.0.0",
		"server.thread_pool": 10,
		"log.screen": False}
		}

	cherrypy.config.update(config)

	config = {"/": {
		"tools.gzip.on": True}
		}

	cherrypy.tree.mount(Root(), "/", config)
	cherrypy.engine.start()

if __name__ == "__main__":
	main()
