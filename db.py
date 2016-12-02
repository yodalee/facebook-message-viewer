import sqlite3
import unittest

def createdb():
    userdb = sqlite3.connect("user.db", detect_types=sqlite3.PARSE_DECLTYPES)

    userdb.execute("CREATE TABLE IF NOT EXISTS dbUser (" \
            "id INTEGER PRIMARY KEY," \
            "file BLOB," \
            "isReady INTEGER)")

    userdb.execute("CREATE TABLE IF NOT EXISTS dbGroup (" \
            "userid INTEGER REFERENCES dbUser(id)," \
            "members TEXT)")

    userdb.execute("CREATE TABLE IF NOT EXISTS dbMessage (" \
            "groupid INTEGER REFERENCES dbGroup(id)," \
            "author TEXT," \
            "time TIMESTAMP," \
            "content TEXT)")

    userdb.close()
