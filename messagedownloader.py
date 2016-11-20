#-*- coding: UTF-8 -*-
#/usr/bin/env python
import sys
import os
import logging
import json
import datetime
import subprocess

import sqlite3
import jinja2
from bottle import route
from bottle import run
from bottle import template
from bottle import static_file
from bottle import request
from bottle import abort
from bottle import redirect
from bottle import response

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

    print("lang: {}, filename: {}".format(lang, filename))

    # store database
    db = sqlite3.connect("user.db")
    c = db.cursor()
    query = "INSERT INTO dbUser (file, isReady) VALUES (?, 0)"
    c.execute(query, [sqlite3.Binary(file_content)])
    userid = str(c.lastrowid)

    db.commit()

    # invoke another process to processing
    subprocess.call(['python2.7', 'worker.py', lang, userid])

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


@route('/fetch')
def MessageFetchHandler():
    reqType = request.query.type
    print("API request type: {}".format(reqType))
    userid = 1
    db = sqlite3.connect("user.db")
    c = db.cursor()

    response.content_type = "application/json"

    if reqType == "user":
        pass
    elif reqType == "groups":
        c.execute('SELECT members FROM dbGroup WHERE userid=?', (userid,))
        groups = [i[0] for i in c.fetchall()]
        print("Get {} groups".format(len(groups)))
        return json.dumps({"groups": groups})

    elif reqType == "message":
        groupname = request.query.group
        startstr = request.query.startdate
        startdate = datetime.datetime.strptime(startstr or "20010101", "%Y%m%d")
        endstr = request.query.enddate
        if endstr:
            enddate = datetime.datetime.strptime(endstr, "%Y%m%d")
        else:
            enddate = datetime.datetime.today()

        c.execute('SELECT rowid FROM dbGroup WHERE members=?', (groupname,))
        groupid = c.fetchone()[0]

        c.execute('SELECT * FROM dbMessage WHERE groupid=?', (groupid,))
        msgQuery = c.fetchmany(300)

        ret = [{"author": msg[1],
            "time": msg[2],
            "content": msg[3]} for msg in msgQuery]

        return json.dumps({"messages": ret})

run(host='localhost', port=8080, reloader=True)
