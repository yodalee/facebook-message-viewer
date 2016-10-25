#-*- coding: UTF-8 -*-
#/usr/bin/env python
import sys

import webapp2
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers

reload(sys)
sys.setdefaultencoding("utf-8")

# Basic datastruct in user blob
class UserMessage(ndb.Model):
    user = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()


class MessageUploadFormHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]
            user_message = UserMessage(
                user=users.get_current_user().user_id(),
                blob_key=upload.key())
            user_message.put()

            self.redirect('/view')

        except:
            self.error(500)


class MessageUploadForm(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/uploadhandler')
        self.response.out.write("""
<html><body>
<form action="{0}" method="POST" enctype="multipart/form-data">
    Upload Message.htm: <input type="file" name="file"><br>
    <input type="submit" name="submit" value="Submit">
</form>
</body></html>""".format(upload_url))


class MessageViewHandler(webapp2.RequestHandler):
    def get(self):
        query = UserMessage.query(
                UserMessage.user == users.get_current_user().user_id())
        msgblob = query.fetch()
        if len(msgblob) == 0:
            self.redirect('upload')

        self.response.out.write("Hello World!")


class RedirectHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/view')

app = webapp2.WSGIApplication([
    ('/view', MessageViewHandler),
    ('/upload', MessageUploadForm),
    ('/uploadhandler', MessageUploadFormHandler),
    ('/.*', RedirectHandler),
], debug=True)
