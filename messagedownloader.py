#-*- coding: UTF-8 -*-
#/usr/bin/env python
import json
from multiprocessing import Process

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
from dbSqlite3 import dbSqlite3

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader('template'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

database = dbSqlite3()
parser = ParseHandler()

def MessageUploadFormHandler():
    lang = request.forms.get('lang')
    data = request.files.get('file')
    filename = data.filename
    file_content = data.file.read()

    print("lang: {}, filename: {}".format(lang, filename))

    parser.setLang(lang)
    if not parser.isValid(file_content):
        print("The uploaded file not valid")
        redirect('/view')

    # simple check OK, parse username store database
    username = parser.parseUsername()
    userid = database.insertUser(username)

    # invoke another process to processing
    p = Process(target = parser.parse, args=(userid,))
    p.start()

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

    response.content_type = "application/json"

    if reqType == "user":
        pass
    elif reqType == "groups":
        groupquery = database.getGroup(userid)
        groups = [i[1] for i in groupquery]
        print("Get {} groups".format(len(groups)))
        return json.dumps({"groups": groups})

    elif reqType == "message":
        groupname = request.query.group
        startstr = request.query.startdate
        endstr = request.query.enddate

        # fetch database
        messages = database.getMessage(groupname, startstr, endstr)
        friendmap = dict(database.getFriend(userid))

        # prepare message
        ret = [{"author": friendmap.get(msg[1]),
            "time": msg[2],
            "content": msg[3]} for msg in messages]
        return json.dumps({"messages": ret})

    elif reqType == "friend":
        userid = request.query.userid
        oldName = request.query.old
        newName = request.query.new
        database.updateFriend(userid, oldName, newName)

def setup_routing(app):
    app.route('/', 'GET', MessageViewHandler)
    app.route('/view', 'GET', MessageViewHandler)
    app.route('/uploadhandler', 'POST', MessageUploadFormHandler)
    app.route('/upload', 'GET', MessageUploadForm)
    app.route('/static/<path:path>', 'GET', callback)
    app.route('/fetch', 'GET', MessageFetchHandler)

if __name__ == "__main__":
    app = Bottle()
    setup_routing(app)
    run(app=app, host='localhost', port=8080, reloader=True)
