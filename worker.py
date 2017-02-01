# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime
from lxml import etree
from io import BytesIO

from config import REdict
from dbSqlite3 import dbSqlite3

database = dbSqlite3()
logging.basicConfig(level=logging.INFO)

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
        logging.info("{} initial parse check: {}".format(time.time(), self.lang["showName"]))

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
        logging.info("{}, Parse username: {}".format(time.time(), username))
        return username

    def parseUserid(self):
        username = self.xpathUser(self.content)[0].strip()
        threads = self.xpathThread(self.content)
        ll = []
        for thread in threads:
            members = list(map(
                lambda x: x.strip().rstrip('@facebook.com'),
                thread.text.split(',')))

            if username not in members:
                ll.extend(members)

        userfbid = max(ll or [0], key=ll.count)
        logging.info("{}, Parse userfbid: {}".format(time.time(), userfbid))
        return userfbid

    def parseGroup(self, threads, userid):
        """parseGroup: parse through all group and build a table
           to all username in this message file
        """
        # build dictionary
        friendset = set()
        for thread in threads:
            friendset |= set(map(lambda x: x.strip(), thread.text.split(',')))

        logging.info("{}, Parse all friend, got {} unique friend name".format(
            time.time(), len(friendset)))

        # store friendlist
        friendlist = [(userid, name, name) for name in friendset]
        database.insertFriend(friendlist)

        return friendset

    def parseMessage(self, threads, userid, grouplist):
        # variable
        groupnum = len(threads)
        processed = 0
        idx = 0
        msgbuf = [None] * 512
        subtime = 0
        prevtime = datetime(2001, 1, 1)

        logging.info("{}, Parse message start".format(time.time()))

        for thread in threads:
            gname = thread.text.strip()

            if gname in grouplist:
                groupid = grouplist[gname]
            else:
                groupid = database.insertGroup(userid, gname, gname)
                grouplist[gname] = groupid

            logging.info("Process id {}: {}, process {}/{}".format(
                groupid, gname, processed, groupnum))

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

                msgbuf[idx] = (userid, groupid, author, msgtime, subtime, text)

                idx = idx + 1
                if idx == 512:
                    idx = 0
                    database.insertMessage(msgbuf)

            processed = processed + 1

        if idx != 0:
            database.insertMessage(msgbuf[:idx])


    def parse(self, userid):
        starttime = time.time()
        logging.info("{}, process start user_id: {}, lang: {}".format(
            time.time(), userid, self.lang["showName"]))

        threads = self.xpathThread(self.content)

        # insert userid
        userfbid = self.parseUserid()

        # built friend table
        self.parseGroup(threads, userid)

        # prepare group
        existGroup = database.getGroup(userid)
        grouplist = dict()
        for (groupid, gname, _) in existGroup:
            grouplist[gname] = groupid

        # process message
        self.parseMessage(threads, userid, grouplist)

        # process end
        endtime = time.time()
        logging.info("{} Process end, time consumed: {}".format(endtime, endtime-starttime))

        # update user info
        database.updateUser(userid)
