#-*- coding: UTF-8 -*-
#/usr/bin/env python
import sys
import os
import logging
import json
import datetime

import jinja2
from bottle import route, run, template, static_file

from config import REdict

reload(sys)
sys.setdefaultencoding("utf-8")

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader('template'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


@route('/uploadhandler')
def MessageUploadFormHandler():
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

@route('/upload')
def MessageUploadForm():
    template = JINJA_ENVIRONMENT.get_template('upload.html')
    template_values = {
        'upload_url': '/uploadhandler',
        'langs': REdict,
    }
    return template.render(template_values)

@route('/')
@route('/view')
def MessageViewHandler():
    template = JINJA_ENVIRONMENT.get_template('view.html')
    return template.render()

@route('/static/<path:path>')
def callback(path):
    return static_file(path, root='static')


def MessageFetchHandler():
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


run(host='localhost', port=8080)
