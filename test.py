#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, timedelta
import string

import random

from config import REdict, REdictTest
from worker import ParseHandler
from dbSqlite3 import dbSqlite3

class ParseHandlerTest(unittest.TestCase):
    def setUp(self):
        with open("testcase/test-en.htm", "rb") as f:
            self.parser = ParseHandler()
            self.parser.setLang("en")
            content = f.read()
            self.parser.isValid(content)

    def test_parseUsername(self):
        username = self.parser.parseUsername()
        self.assertEqual(username, "葉闆")

    def test_parseUserid(self):
        username = self.parser.parseUserid()
        self.assertEqual(username, "100000000000000")

class dbSqlite3Test(unittest.TestCase):
    def setUp(self):
        self.content = bytes("testcontent", "utf-8")
        self.database = dbSqlite3()
        self.userid = self.database.insertUser("testuser")

    def strgen(self, size=10):
        return ''.join(random.choice(string.ascii_lowercase) \
            for _ in range(size))

    def testFriend(self):
        insertnum = random.randrange(10, 20)
        friends = [self.strgen() for _ in range(insertnum)]

        # insert friend and check exist
        for friend in friends:
            self.database.insertFriend(self.userid, friend, friend)
        result = self.database.getFriend(self.userid)
        self.assertEqual(len(result), insertnum)

        # update
        oldName, newName = random.choice(friends), self.strgen()
        self.database.updateFriend(
            self.userid, oldName, newName)

        # get
        result = self.database.getFriend(self.userid)
        for ret in result:
            if ret[0] == oldName:
                self.assertEqual(ret[1], newName)

    def testGroup(self):
        insertnum = random.randrange(10, 20)
        groups = [self.strgen() for _ in range(insertnum)]

        # insert group and check exist
        for group in groups:
            self.database.insertGroup(self.userid, group)

        result = self.database.getGroup(self.userid)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), insertnum)
        self.assertListEqual([i for (_, i) in result], groups)

    def testMessage(self):
        # generate messages in three groups 2008 grp1 2010 grp2 2012 grp3
        insertnum = [random.randrange(10, 20) for _ in range(3)]
        groupname = self.strgen()
        groupid = self.database.insertGroup(self.userid, groupname)
        author = self.strgen()
        starttime = datetime(2008, 1, 1)
        msgbuf = []
        count = 0
        for i, n in enumerate(insertnum):
            for _ in range(n):
                t = starttime + timedelta(
                    days = random.randrange(365*2*i, 365*2*(i+1)))
                msgbuf.append((self.userid, groupid, author, t, 0, self.strgen(500)))
        self.database.insertMessage(msgbuf)

        # test query
        get = self.database.getMessage(self.userid, groupname, None, "20100101")
        self.assertEqual(len(get), insertnum[0])
        get = self.database.getMessage(self.userid, groupname, "20100101", "20120101")
        self.assertEqual(len(get), insertnum[1])
        get = self.database.getMessage(self.userid, groupname, "20120101", None)
        self.assertEqual(len(get), insertnum[2])

    def testSameTime(self):
        groupname = self.strgen()
        groupid = self.database.insertGroup(self.userid, groupname)
        author = self.strgen()
        msgbuf = []
        for i in range(3):
            msgbuf.append((
                self.userid, groupid, author,
                datetime(2008, 1, 1), i,
                "message{}".format(i)))
        self.database.insertMessage(msgbuf)

        get = self.database.getMessage(self.userid, groupname)
        for i in range(len(msgbuf)):
            self.assertEqual("message{}".format(i), get[len(msgbuf)-i-1][3])

    def tearDown(self):
        query = "DELETE FROM dbUser WHERE username = 'testuser'"
        self.database.db.execute(query)
        query = "DELETE FROM dbFriend WHERE userid = ?"
        self.database.db.execute(query, (self.userid,))
        # clear message if exist
        query = "SELECT id FROM dbGroup WHERE userid = ?"
        self.database.cursor.execute(query, (self.userid,))
        groupid = self.database.cursor.fetchone()
        if groupid:
            groupid = groupid[0]
            query = "DELETE FROM dbMessage WHERE groupid = ?"
            self.database.db.execute(query, (groupid,))
        query = "DELETE FROM dbGroup WHERE userid = ?"
        self.database.db.execute(query, (self.userid,))
        self.database.db.commit()

class REdictParseTest(unittest.TestCase):
    pass

def testParseGen(k, v):
    def test(self):
        timetext = REdictTest[k]["q"].rsplit(" ", 1)[0]
        parse = datetime.strptime(timetext, v["parseStr"])
        ans = REdictTest[k]["a"]
        assert(ans == parse)
    return test

def main():
    for k,v in REdict.items():
        test_func = testParseGen(k, v)
        setattr(REdictParseTest, "test_%s" % (k), test_func)
    unittest.main()

if __name__ == "__main__":
    main()
