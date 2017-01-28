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

def MessageViewHandler():
    template = JINJA_ENVIRONMENT.get_template('view.html')
    template_values = {
        'upload_url': '/uploadhandler',
        'langs': REdict,
    }
    return template.render(template_values)

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
        groups = [{"name": grp[1], "nickname": grp[2]} for grp in groupquery]
        print("Get {} groups".format(len(groups)))
        return json.dumps({"groups": groups})

    elif reqType == "message":
        groupname = request.query.group
        startstr = request.query.startdate
        endstr = request.query.enddate

        # fetch database
        messages = database.getMessage(userid, groupname, startstr, endstr)

        # prepare message
        ret = [{"name": msg[0],
            "nickname": msg[1],
            "time": msg[2],
            "content": msg[3]} for msg in messages]
        return json.dumps({"messages": ret})

    elif reqType == "date":
        groupname = request.query.groups
        dates = database.getDate(userid, groupname)
        dates = list(set(map(lambda x: x[0].split()[0], dates)))

        return json.dumps({"dates": dates})

    elif reqType == "friend":
        fname = request.query.fname
        fnickname = request.query.fnickname
        oldfnick = None

        # find old nickname
        friendquery = database.getFriend(userid)
        for fitem in friendquery:
            if fname == fitem[0]:
                oldfnick = fitem[1]
                break;

        # update friend's nickname
        database.updateFriend(userid, fname, fnickname)

        # update group that contain fname
        groupquery = database.getGroup(userid)
        for g in filter(lambda x: fname in x[1], groupquery):
            gname, gnickname = g[1], g[2].replace(oldfnick, fnickname)
            database.updateGroup(userid, gname, gnickname)

def setup_routing(app):
    app.route('/', 'GET', MessageViewHandler)
    app.route('/view', 'GET', MessageViewHandler)
    app.route('/uploadhandler', 'POST', MessageUploadFormHandler)
    app.route('/static/<path:path>', 'GET', callback)
    app.route('/fetch', 'GET', MessageFetchHandler)

if __name__ == "__main__":
    app = Bottle()
    setup_routing(app)
    run(app=app, host='localhost', port=8080, reloader=True)
