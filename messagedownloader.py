#-*- coding: UTF-8 -*-
#/usr/bin/env python
import sys
import os
import logging
import json
import datetime

import sqlite3
import jinja2
from bottle import route
from bottle import run
from bottle import template
from bottle import static_file
from bottle import request
from bottle import abort
from bottle import redirect

from config import REdict

reload(sys)
sys.setdefaultencoding("utf-8")

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader('template'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


@route('/uploadhandler', method="POST")
def MessageUploadFormHandler():
    lang = request.forms.get(u'lang')
    data = request.files.file
    filename = data.filename
    file_content = data.file.read()

    db = sqlite3.connect("user.db")
    c = db.cursor()
    query = "INSERT INTO dbUser (file, isReady) VALUES (?, 0)"
    db.execute(query, [sqlite3.Binary(file_content)])
    db.commit()

    print("lang: {}, filename: {}".format(lang, filename))

    redirect('/view')

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

run(host='localhost', port=8080, reloader=True)
