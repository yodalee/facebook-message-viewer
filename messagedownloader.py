#-*- coding: UTF-8 -*-
#/usr/bin/env python
import sys

import webapp2
from google.appengine.api import users

reload(sys)
sys.setdefaultencoding("utf-8")

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.headers["Content-Type"] = "text/plain"
        self.response.write("Hello, {0}\n".format(user.nickname()))

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
