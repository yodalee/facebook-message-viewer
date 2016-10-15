#-*- coding: UTF-8 -*-
#/usr/bin/env python
import sys

import logging
import json
import random
import urllib2

import webapp2

reload(sys)
sys.setdefaultencoding("utf-8")

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain"
        self.response.write("Hello, World!")

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
