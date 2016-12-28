import db

import sqlite3
import unittest
import datetime

class dbSqlite3(db.db):
    """Database abstraction for sqlite3"""

    def __init__(self):
        self.db = self.createdb()
        self.cursor = self.db.cursor()

    def createdb(self):
        db = sqlite3.connect("user.db")

        db.execute("CREATE TABLE IF NOT EXISTS dbUser (" \
            "id INTEGER PRIMARY KEY," \
            "file BLOB," \
            "isReady INTEGER)")

        db.execute("CREATE TABLE IF NOT EXISTS dbGroup (" \
            "userid INTEGER REFERENCES dbUser(id)," \
            "members TEXT)")

        db.execute("CREATE TABLE IF NOT EXISTS dbMessage (" \
            "groupid INTEGER REFERENCES dbGroup(id)," \
            "author TEXT," \
            "time TIMESTAMP," \
            "content TEXT)")

        return db

    def getUpload(self, userid):
        # get upload data
        self.cursor.execute("SELECT file FROM dbUser " \
                "WHERE id == %d" % (userid))
        data = self.cursor.fetchone()
        return data[0]

    def updateUser(self, userid):
        self.cursor.execute("UPDATE dbUser SET isReady = 1 " \
            "WHERE id == %d" % (userid))
        self.db.commit()

    def insertUser(self, content):
        """create entry of user

        :content: raw content uploaded by user
        :return: userid of the inserted id

        """
        query = "INSERT INTO dbUser (file, isReady) VALUES (?, 0)"
        self.cursor.execute(query, [sqlite3.Binary(content)])
        userid = str(self.cursor.lastrowid)
        self.db.commit()

        return userid

    def insertGroup(self, userid, groupname):
        self.cursor.execute("INSERT INTO dbGroup (userid, members) " \
                "VALUES (?, ?)", (userid, groupname))
        groupid = self.cursor.lastrowid
        self.db.commit()
        return groupid

    def insertMessage(self, msgbuf):
        """insert array of message object into database

        :msgbuf: array of tuple that contain: (groupid, author, msgtime, text)
        """
        self.cursor.executemany("INSERT OR IGNORE INTO dbMessage " \
                "(groupid, author, time, content) VALUES (?,?,?,?)",
                msgbuf)

    def getGroup(self, userid):
        self.cursor.execute('SELECT members FROM dbGroup WHERE userid=?', (userid,))
        return [i[0] for i in self.cursor.fetchall()]

    def getUser(self, groupname, startstr, endstr):
        startdate = datetime.datetime.strptime(startstr or "20010101", "%Y%m%d")
        if endstr:
            enddate = datetime.datetime.strptime(endstr, "%Y%m%d")
        else:
            enddate = datetime.datetime.today()

        self.cursor.execute("SELECT rowid FROM dbGroup " \
            "WHERE members=?", (groupname,))
        groupid = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT * FROM dbMessage " \
            "WHERE groupid=? AND time >= ? AND time < ?" \
            "ORDER BY time", (groupid, startdate, enddate, ))

        return self.cursor.fetchmany(30)