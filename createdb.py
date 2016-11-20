import sqlite3
import unittest

db = sqlite3.connect("user.db")
db.execute("CREATE TABLE dbUser (" \
        "id INTEGER PRIMARY KEY," \
        "file BLOB," \
        "isReady INTEGER)")

# class dbGroup(ndb.Model):
#     user_key = ndb.KeyProperty(kind=dbUser, required=True)
#     group = ndb.StringProperty()
# 
# 
# class dbMessage(ndb.Model):
#     group_key = ndb.KeyProperty(kind=dbGroup, required=True)
#     author = ndb.StringProperty()
#     time = ndb.DateTimeProperty()
#     content = ndb.TextProperty()

