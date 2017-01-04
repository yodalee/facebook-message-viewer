#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import datetime
import string
import random

from config import REdict, REdictTest
from worker import ParseHandler
from dbSqlite3 import dbSqlite3

class ParseHanderTest(unittest.TestCase):
    def setUp(self):
        with open("testcase/test-en.htm", "rb") as f:
            self.parser = ParseHandler()
            self.content = f.read()

    def test_parseUsername(self):
        username = self.parser.parseUsername(self.content)
        self.assertEqual(username, "葉闆")

class dbSqlite3Test(unittest.TestCase):
    def setUp(self):
        self.content = bytes("testcontent", "utf-8")
        self.database = dbSqlite3()
        self.userid = self.database.insertUser(
            "testuser", self.content)

    def testGetUpload(self):
        storedvalue = self.database.getUpload(self.userid)
        self.assertEqual(storedvalue, self.content)

    def strgen(self, size=10):
        return ''.join(random.choice(string.ascii_lowercase) \
            for _ in range(size))

    def testFriend(self):
        insertnum = random.randrange(10, 20)
        friends = [self.strgen() for _ in range(insertnum)]

        # insert friend and check exist
        for friend in friends:
            self.database.insertFriend(self.userid, friend)
        query = "SELECT originName, modifyName " \
                "FROM dbFriend WHERE userid = %d" % self.userid
        self.database.cursor.execute(query)
        result = self.database.cursor.fetchall()
        self.assertEqual(len(result), insertnum)

        # update
        oldName, newName = random.choice(friends), self.strgen()
        self.database.updateFriend(
            self.userid, oldName, newName)

        query = "SELECT modifyName FROM dbFriend " \
                "WHERE userid = ? AND originName = ?"
        self.database.cursor.execute(query, (self.userid, oldName))
        result = self.database.cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], newName)


    def tearDown(self):
        query = "DELETE FROM dbUser WHERE username = 'testuser'"
        self.database.db.execute(query)
        query = "DELETE FROM dbFriend WHERE userid = ?"
        self.database.cursor.execute(query, (self.userid,))
        self.database.db.commit()

class REdictParseTest(unittest.TestCase):
    pass

def testParseGen(k, v):
    def test(self):
        timetext = REdictTest[k]["q"].rsplit(" ", 1)[0]
        parse = datetime.datetime.strptime(timetext, v["parseStr"])
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
