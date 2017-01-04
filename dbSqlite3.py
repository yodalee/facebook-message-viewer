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
            "file BLOB," \
            "username TEXT," \
            "isReady INTEGER)")

        # dbFriend table to friend list, deal with id@facebook.com
        db.execute("CREATE TABLE IF NOT EXISTS dbFriend (" \
            "userid INTEGER REFERENCES dbUser(id)," \
            "originName TEXT," \
            "modifyName TEXT," \
            "UNIQUE (userid, originName))")

        # members store the thread name in record file
        db.execute("CREATE TABLE IF NOT EXISTS dbGroup (" \
            "userid INTEGER REFERENCES dbUser(id)," \
            "id INTEGER PRIMARY KEY," \
            "members TEXT)")

        # dbMessage each message become a entry
        db.execute("CREATE TABLE IF NOT EXISTS dbMessage (" \
            "groupid INTEGER REFERENCES dbGroup(id)," \
            "id INTEGER PRIMARY KEY," \
            "author TEXT," \
            "time TIMESTAMP," \
            "subtime INTEGER," \
            "content TEXT," \
            "UNIQUE (groupid, author, time, content))")

        db.commit()
        return db

    def insertUser(self, username, content):
        """update content or create entry for user

        :content: raw content uploaded by user
        :return: userid of the inserted id

        """
        query = "INSERT OR REPLACE INTO dbUser " \
                "(id, file, username, isReady) " \
                "VALUES (" \
                "(SELECT id FROM dbUser WHERE username = '%s'), " \
                "?, ?, 0)" % (username)
        self.cursor.execute(query, (sqlite3.Binary(content), username))
        userid = str(self.cursor.lastrowid)
        self.db.commit()

        return userid

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

    def insertFriend(self, userid, friendname):
        self.cursor.execute("INSERT or IGNORE INTO dbFriend " \
                "(userid, originName, modifyName) " \
                "VALUES (?, ?, ?)", (userid, friendname, friendname))
        self.db.commit()

    def updateFriend(self, userid, originName, modifyName):
        self.cursor.execute("UPDATE dbFriend " \
                "SET modifyName = ? " \
                "WHERE userid = ?, originName = ?", \
                (userid, friendname, friendname))
        self.db.commit()

    def getFriend(self, userid):
        self.cursor.execute("SELECT recordName FROM dbFriend " \
                "WHERE userid=?", (userid,))
        return self.cursor.fetchall()

    def insertGroup(self, userid, groupname):
        self.cursor.execute("INSERT INTO dbGroup (userid, members) " \
                "VALUES (?, ?)", (userid, groupname))
        groupid = self.cursor.lastrowid
        self.db.commit()
        return groupid

    def getGroup(self, userid):
        self.cursor.execute('SELECT id, members FROM dbGroup " \
                "WHERE userid=?', (userid,))
        return self.cursor.fetchall()

    def insertMessage(self, msgbuf):
        """insert array of message object into database

        :msgbuf: array of tuple that contain: (groupid, author, msgtime, text)
        """
        self.cursor.executemany("INSERT OR IGNORE INTO dbMessage " \
                "(groupid, author, time, subtime, content) " \
                "VALUES (?,?,?,?,?)",
                msgbuf)

    def getMessage(self, groupname, startstr, endstr):
        startdate = datetime.datetime.strptime(startstr or "20010101", "%Y%m%d")
        if endstr:
            enddate = datetime.datetime.strptime(endstr, "%Y%m%d")
        else:
            enddate = datetime.datetime.today()

        self.cursor.execute("SELECT rowid FROM dbGroup " \
            "WHERE members=?", (groupname,))
        groupid = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT id, author, time, content " \
            "FROM dbMessage " \
            "WHERE groupid=? AND time >= ? AND time < ?" \
            "ORDER BY time, subtime DESC",
            (groupid, startdate, enddate, ))

        return self.cursor.fetchmany(30)
