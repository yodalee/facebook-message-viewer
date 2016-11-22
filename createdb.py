import sqlite3
import unittest

userdb = sqlite3.connect("user.db", detect_types=sqlite3.PARSE_DECLTYPES)

userdb.execute("CREATE TABLE dbUser (" \
        "id INTEGER PRIMARY KEY," \
        "file BLOB," \
        "isReady INTEGER)")

userdb.execute("CREATE TABLE dbGroup (" \
        "userid INTEGER REFERENCES dbUser(id)," \
        "members TEXT)")

userdb.execute("CREATE TABLE dbMessage (" \
        "groupid INTEGER REFERENCES dbGroup(id)," \
        "author TEXT," \
        "time TIMESTAMP," \
        "content TEXT)")

userdb.close()
