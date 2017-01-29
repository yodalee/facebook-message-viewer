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

        # dbUser: table about user, uploaded blob, username
        db.execute("CREATE TABLE IF NOT EXISTS dbUser (" \
            "id INTEGER PRIMARY KEY," \
            "username TEXT," \
            "isReady INTEGER)")

        # dbFriend table to friend list, deal with id@facebook.com
        db.execute("CREATE TABLE IF NOT EXISTS dbFriend (" \
            "userid INTEGER REFERENCES dbUser(id)," \
            "fname TEXT," \
            "fnickname TEXT," \
            "UNIQUE (userid, fname))")

        # dbGroup store the thread name in record file
        db.execute("CREATE TABLE IF NOT EXISTS dbGroup (" \
            "userid INTEGER REFERENCES dbUser(id)," \
            "id INTEGER PRIMARY KEY," \
            "gname TEXT," \
            "gnickname TEXT)")

        # dbMessage each message become a entry
        db.execute("CREATE TABLE IF NOT EXISTS dbMessage (" \
            "userid INTEGER REFERENCES dbUser(id)," \
            "groupid INTEGER REFERENCES dbGroup(id)," \
            "id INTEGER PRIMARY KEY," \
            "author TEXT," \
            "time TIMESTAMP," \
            "subtime INTEGER," \
            "content TEXT," \
            "UNIQUE (groupid, author, time, content))")

        db.commit()
        return db

    def insertUser(self, username):
        """update content or create entry for user

        :content: raw content uploaded by user
        :return: userid of the inserted id

        """
        query = "INSERT OR REPLACE INTO dbUser " \
                "(id, username, isReady) " \
                "VALUES (" \
                "(SELECT id FROM dbUser WHERE username = '%s'), " \
                "?, 0)" % (username)
        self.cursor.execute(query, (username,))
        userid = self.cursor.lastrowid
        self.db.commit()

        return userid

    def updateUser(self, userid):
        self.cursor.execute("UPDATE dbUser SET isReady = 1 " \
            "WHERE id == %d" % (userid))
        self.db.commit()

    def insertFriend(self, userid, fname, fnickname):
        self.cursor.execute("INSERT or IGNORE INTO dbFriend " \
                "(userid, fname, fnickname) " \
                "VALUES (?, ?, ?)", (userid, fname, fnickname))
        self.db.commit()

    def updateFriend(self, userid, fname, fnickname):
        self.cursor.execute("UPDATE dbFriend " \
                "SET fnickname = ? " \
                "WHERE userid = ? " \
                "AND fname = ?", (fnickname, userid, fname))
        self.db.commit()

    def getFriend(self, userid):
        self.cursor.execute("SELECT fname, fnickname FROM dbFriend " \
                "WHERE userid=?", (userid,))
        return self.cursor.fetchall()

    def insertGroup(self, userid, gname, gnickname):
        self.cursor.execute("INSERT INTO dbGroup (userid, gname, gnickname) " \
                "VALUES (?, ?, ?)", (userid, gname, gnickname))
        groupid = self.cursor.lastrowid
        self.db.commit()
        return groupid

    def updateGroup(self, userid, gname, gnickname):
        self.cursor.execute("UPDATE dbGroup " \
                "SET gnickname = ? " \
                "WHERE userid = ? " \
                "AND gname = ?", (gnickname, userid, gname))
        self.db.commit()

    def getGroup(self, userid):
        self.cursor.execute('SELECT id, gname, gnickname FROM dbGroup " \
                "WHERE userid=?', (userid,))
        return self.cursor.fetchall()

    def insertMessage(self, msgbuf):
        """insert array of message object into database

        :msgbuf: array of tuple that contain: (groupid, author, msgtime, text)
        """
        self.cursor.executemany("INSERT OR IGNORE INTO dbMessage " \
                "(userid, groupid, author, time, subtime, content) " \
                "VALUES (?,?,?,?,?,?)",
                msgbuf)

    def getMessage(self, userid, gname, startstr=None, endstr=None):
        startdate = datetime.datetime.strptime(startstr or "20010101", "%Y%m%d")
        if endstr:
            enddate = datetime.datetime.strptime(endstr, "%Y%m%d")
        else:
            enddate = datetime.datetime.today()

        self.cursor.execute("SELECT rowid FROM dbGroup " \
            "WHERE gname=?", (gname,))
        groupid = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT " \
            "f.fname, f.fnickname, m.time, m.content " \
            "FROM dbMessage AS m " \
            "LEFT JOIN dbFriend AS f ON " \
                "m.author = f.fname AND m.userid = f.userid " \
            "WHERE m.groupid=? AND m.time >= ? AND m.time < ?" \
            "ORDER BY m.time, m.subtime DESC",
            (groupid, startdate, enddate, ))

        return self.cursor.fetchmany(30)

    def getDate(self, userid, gname):
        self.cursor.execute("SELECT rowid FROM dbGroup " \
            "WHERE gname=?", (gname,))
        groupid = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT time " \
            "FROM dbMessage WHERE groupid=? GROUP BY time", (groupid,))
        return self.cursor.fetchall()
