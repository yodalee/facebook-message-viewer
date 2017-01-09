# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime
from lxml import etree
from io import BytesIO

from config import REdict
from dbSqlite3 import dbSqlite3

database = dbSqlite3()

class ParseHandler():
    def __init__(self):
        self.xpathContent = etree.XPath("//div[@class='contents']")
        self.xpathUser    = etree.XPath(".//h1//text()")
        self.xpathThread  = etree.XPath(".//div[@class='thread']")
        self.xpathMessage = etree.XPath(".//div[@class='message']")
        self.xpathAuthor  = etree.XPath(".//span[@class='user']//text()")
        self.xpathTime    = etree.XPath(".//span[@class='meta']//text()")
        self.xpathText    = etree.XPath(".//p")
        self.parser = etree.HTMLParser(encoding='UTF-8')
        self.lang = None
        self.content = None

    def setLang(self, lang):
        self.lang = REdict[lang]

    def isValid(self, file_content):
        """isLangValid: check uploaded file_content is valid
        """
        logging.info("initial parse check: {}".format(self.lang["showName"]))

        root = etree.parse(BytesIO(file_content), self.parser)

        # process group
        try:
            content = self.xpathContent(root)[0]
            thread = self.xpathThread(content)[0]

            # check extract content safe
            author = self.xpathAuthor(thread)
            timetext = self.xpathTime(thread)
            text = self.xpathText(thread)

            # check languag setting valid
            timetext = timetext[0].strip().rsplit(" ", 1)[0]
            msgtime = datetime.strptime(timetext, self.lang["parseStr"])

            # everything ok, store value
            self.content = content
            return True
        except Exception as e:
            print(e)
            return False

    def parseUsername(self):
        username = self.xpathUser(self.content)[0].strip()
        logging.info("Parse username: {}".format(username))
        return username

    def parseGroup(self, threads, userid):
        """parseGroup: parse through all group and build a table
           to all username in this message file
        """
        # build dictionary
        friendset = set()
        idx = 0
        for thread in threads:
            friendset |= set(map(lambda x: x.strip(), thread.text.split(',')))

        logging.info("Parse all friend, got {} unique friend name".format(
            len(friendset)))

        # store friendlist
        for name in friendset:
            database.insertFriend(userid, name, name)

    def parse(self, userid):
        logging.info("user_id: {}, lang: {}".format(userid, self.lang["showName"]))
        starttime = time.time()

        threads = self.xpathThread(self.content)

        # built friend table
        self.parseGroup(threads, userid)

        # prepare group
        existGroup = database.getGroup(userid)
        grouplist = dict()
        for (groupid, members) in existGroup:
            grouplist[members] = groupid
        groupnum = len(threads)

        # variable
        processed = 0
        idx = 0
        msgbuf = [None] * 512
        subtime = 0
        prevtime = datetime(2001, 1, 1)

        print("Process message start")
        starttime = time.time()

        for thread in threads:
            members = thread.text.strip()

            if members in grouplist:
                groupid = grouplist[members]
            else:
                groupid = database.insertGroup(userid, members)
                grouplist[members] = groupid

            print("Process id {}: {}, progress {}/{}".format(
                groupid, members, processed, groupnum))

            authorlist = self.xpathAuthor(thread)
            timelist = self.xpathTime(thread)
            textlist = self.xpathText(thread)

            for author, timetext, text in zip(authorlist, timelist, textlist):
                author = author.strip()

                # cut down last string "UTC+08"
                # which cause dateparser failed to parse
                timetext = timetext.strip().rsplit(" ", 1)[0]
                msgtime = datetime.strptime(timetext, self.lang["parseStr"])
                if msgtime == prevtime:
                    subtime = subtime + 1
                else:
                    prevtime = msgtime
                    subtime = 0
                text = (text.text or "").strip()

                msgbuf[idx] = (groupid, author, msgtime, subtime, text)

                idx = idx + 1
                if idx == 512:
                    idx = 0
                    database.insertMessage(msgbuf)

            processed = processed + 1

        if idx != 0:
            database.insertMessage(msgbuf[:idx])

        # process end
        endtime = time.time()
        print("Process end, time consumed: {}".format(endtime-starttime))

        # update user info
        database.updateUser(userid)
