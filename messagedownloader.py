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
from bottle import Bottle
from bottle import route
from bottle import run
from bottle import template
from bottle import static_file
from bottle import request
from bottle import abort
from bottle import redirect
from bottle import response

from config import REdict
from worker import ParseHandler

reload(sys)
sys.setdefaultencoding("utf-8")

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader('template'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def MessageUploadFormHandler():
    lang = request.forms.get(u'lang')
    data = request.files.file
    filename = data.filename
    file_content = data.file.read()

    print("lang: {}, filename: {}".format(lang, filename))

    # do simple check
    handler = ParseHandler()
    try:
        handler.simpleCheck(file_content, lang)
    except Exception as e:
        print(e)
        redirect('/view')

    # simple check OK, store database
    db = sqlite3.connect("user.db")
    c = db.cursor()
    query = "INSERT INTO dbUser (file, isReady) VALUES (?, 0)"
    c.execute(query, [sqlite3.Binary(file_content)])
    userid = str(c.lastrowid)
    db.commit()
    db.close()

    # invoke another process to processing
    popen = subprocess.Popen(['python2.7', 'worker.py', lang, userid])

    redirect('/view')

def MessageUploadForm():
    template = JINJA_ENVIRONMENT.get_template('upload.html')
    template_values = {
        'upload_url': '/uploadhandler',
        'langs': REdict,
    }
    return template.render(template_values)

def MessageViewHandler():
    template = JINJA_ENVIRONMENT.get_template('view.html')
    return template.render()

def callback(path):
    return static_file(path, root='static')

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

        c.execute("SELECT rowid FROM dbGroup WHERE members=?", (groupname,))
        groupid = c.fetchone()[0]

        c.execute("SELECT * FROM dbMessage " \
            "WHERE groupid=? AND time >= ? AND time < ?" \
            "ORDER BY time", (groupid, startdate, enddate, ))
        msgQuery = c.fetchmany(300)

        ret = [{"author": msg[1],
            "time": msg[2],
            "content": msg[3]} for msg in msgQuery]

        return json.dumps({"messages": ret})

def setup_routing(app):
    app.route('/', 'GET', MessageViewHandler)
    app.route('/view', 'GET', MessageViewHandler)
    app.route('/uploadhandler', 'POST', MessageUploadFormHandler)
    app.route('/upload', 'GET', MessageUploadForm)
    app.route('/static/<path:path>', 'GET', callback)
    app.route('/fetch', 'GET', MessageFetchHandler)

app = Bottle()
setup_routing(app)
run(app=app, host='localhost', port=8080, reloader=True)
