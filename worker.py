from google.appengine.ext import ndb
import webapp2
import logging

from dbmodel import UserMessage

class ParseHandler(webapp2.RequestHandler):
    def post(self):
        blob_key = self.request.get('blob_key')
        url_str = self.request.get('user_key')
        logging.info("blob_key: {}, user_key: {}".format(blob_key, url_str))

        user_key = ndb.Key(urlsafe=url_str)
        # fetch the blob

        # start processing

        # update user info
        userdata = user_key.get()
        userdata.isReady = True
        userdata.put()


app = webapp2.WSGIApplication([
    ('/parse', ParseHandler)
    ], debug=True)

