#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import datetime

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
        self.database = dbSqlite3()
        self.database.insertUser("testuser", bytes("testcontent", "utf-8"))

    def test(self):
        pass

    def tearDown(self):
        query = "DELETE FROM dbUser WHERE username = 'testuser'"
        self.database.db.execute(query)
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
