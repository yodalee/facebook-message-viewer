# -*- coding: utf-8 -*-
import time
import logging
from lxml import etree
import datetime
from io import BytesIO

from config import REdict
from dbSqlite3 import dbSqlite3

database = dbSqlite3()

class ParseHandler():
    xpathContent = etree.XPath("//div[@class='contents']")
    xpathThread  = etree.XPath(".//div[@class='thread']")
    xpathMessage = etree.XPath(".//div[@class='message']")
    xpathAuthor  = etree.XPath(".//span[@class='user']//text()")
    xpathTime    = etree.XPath(".//span[@class='meta']//text()")
    xpathText    = etree.XPath(".//p")

    def simpleCheck(self, file_content, lang):
        logging.info("initial parse check lang: {}".format(lang))

        parser = etree.HTMLParser(encoding='UTF-8')
        root = etree.parse(BytesIO(file_content), parser)

        # process group
        content = self.xpathContent(root)[0]

        # start processing
        thread = self.xpathThread(content)[0]
        timetext = self.xpathTime(thread)[0]
        timetext = timetext.strip().rsplit(" ", 1)[0]
        msgtime = datetime.datetime.strptime(timetext, REdict[lang]["parseStr"])

    def parse(self, lang, userid):
        logging.info("user_id: {}, lang: {}".format(userid, lang))

        s = database.getUpload(userid)

        # prepare parser
        parser = etree.HTMLParser(encoding='UTF-8')
        root = etree.parse(BytesIO(s), parser)
        content = self.xpathContent(root)[0]
        threads = self.xpathThread(content)

        # process group
        grouplist = dict()
        groupnum = len(threads)
        processed = 0
        idx = 0
        msgbuf = [None] * 512

        # process group, user name
        for thread in threads:
            members = thread.text.strip()



        # start processing message
        print("Process start")
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
                msgtime = datetime.datetime.strptime(
                        timetext, REdict[lang]["parseStr"])

                text = (text.text or "").strip()

                msgbuf[idx] = (groupid, author, msgtime, text)

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
