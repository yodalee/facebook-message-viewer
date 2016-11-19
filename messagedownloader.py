#-*- coding: UTF-8 -*-
#/usr/bin/env python
import sys
import os
import logging
import json
import datetime

import webapp2
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers

import jinja2

from dbmodel import dbUser, dbGroup, dbMessage
from config import REdict

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
            lang = self.request.params.get(u'lang') # have to use unicode for unknown reason

            logging.info("blob_key: {}, user_id: {}, lang: {}".format(
                blob_key, user_id, lang))
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
                    'user_key':user_key.urlsafe(),
                    'lang'    :lang
                }
            )

            self.redirect('/view')

        except:
            self.error(500)


class MessageUploadForm(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/uploadhandler')
        template = JINJA_ENVIRONMENT.get_template('upload.html')
        template_values = {
            'upload_url': upload_url,
            'langs': REdict,
        }
        self.response.write(template.render(template_values))

class MessageViewHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('view.html')
        self.response.write(template.render())


class MessageFetchHandler(webapp2.RequestHandler):
    def get(self):
        reqType = self.request.get("type")
        print("API request type: {}".format(reqType))
        user_id = users.get_current_user().user_id()
        userdata = dbUser.query(dbUser.user == user_id).fetch()

        self.response.headers['Content-Type'] = "application/json"

        if reqType == "user":
            if not userdata or not userdata[0].isReady:
                self.response.out.write(json.dumps({"user": []}))
            else:
                self.response.out.write(json.dumps({"user": userdata[0].user}))
        elif reqType == "groups":
            dbGroupList = dbGroup.query(dbGroup.user_key == userdata[0].key).fetch()
            groups = [i.group for i in dbGroupList]
            print("Get {} groups".format(len(groups)))
            self.response.out.write(json.dumps({"groups": groups}))

        elif reqType == "message":
            groupname = self.request.get("group")
            startstr = self.request.get("startdate")
            startdate = datetime.datetime.strptime(startstr or "20010101", "%Y%m%d")
            endstr = self.request.get("enddate")
            if endstr:
                enddate = datetime.datetime.strptime(endstr, "%Y%m%d")
            else:
                enddate = datetime.datetime.today()

            group = dbGroup.query(dbGroup.group == groupname).fetch()[0]

            msgQuery = dbMessage.query(
                ndb.AND(dbMessage.group_key == group.key,
                    dbMessage.time > startdate,
                    dbMessage.time < enddate)).order(dbMessage.time).fetch()

            ret = [{"author": msg.author,
                "time": msg.time.strftime("%Y-%m-%d %H:%M"),
                "content": msg.content} for msg in msgQuery]

            self.response.out.write(json.dumps({"messages": ret}))


class RedirectHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/view')

app = webapp2.WSGIApplication([
    ('/view', MessageViewHandler),
    ('/fetch', MessageFetchHandler),
    ('/upload', MessageUploadForm),
    ('/uploadhandler', MessageUploadFormHandler),
    ('/.*', RedirectHandler),
], debug=True)
