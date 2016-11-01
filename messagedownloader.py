#-*- coding: UTF-8 -*-
#/usr/bin/env python
import sys
import os
import logging

import webapp2
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers

import jinja2

from dbmodel import dbUser, dbGroup, dbMessage

JINJA_ENVIRONMENT = jinja2.Environment(
        loader = jinja2.FileSystemLoader('template'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

reload(sys)
sys.setdefaultencoding("utf-8")


class MessageUploadFormHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]
            blob_key = upload.key()
            user_id = users.get_current_user().user_id()

            logging.info("blob_key: {}, user_id: {}".format(blob_key, user_id))
            logging.info("{}".format(type(blob_key)))

            user_message = dbUser(
                user=user_id,
                isReady=False,
                blob_key=blob_key)
            user_key = user_message.put()

            task = taskqueue.add(
                url='/parse',
                params={
                    'blob_key':blob_key,
                    'user_key':user_key.urlsafe()})

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
        user_id = users.get_current_user().user_id()
        query = dbUser.query(dbUser.user == user_id)
        userdata = query.fetch()
        template_values = {
            'userExist': True,
            'hasData': True,
        }
        if len(userdata) == 0:
            template_values['userExist'] = False
        else:
            template_values['hasData'] = userdata[0].isReady

        template = JINJA_ENVIRONMENT.get_template('view.html')
        self.response.write(template.render(template_values))


class RedirectHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/view')

app = webapp2.WSGIApplication([
    ('/view', MessageViewHandler),
    ('/upload', MessageUploadForm),
    ('/uploadhandler', MessageUploadFormHandler),
    ('/.*', RedirectHandler),
], debug=True)
