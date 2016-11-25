# -*- coding: utf-8 -*-
import time
import logging
from lxml import etree
import sys
import datetime
import sqlite3
from StringIO import StringIO

from config import REdict

reload(sys)
sys.setdefaultencoding("utf-8")


class ParseHandler():
    xpathContent = etree.XPath("//div[@class='contents']")
    xpathThread  = etree.XPath(".//div[@class='thread']")
    xpathMessage = etree.XPath(".//div[@class='message']")
    xpathAuthor  = etree.XPath(".//span[@class='user']//text()")
    xpathTime    = etree.XPath(".//span[@class='meta']//text()")
    xpathText    = etree.XPath(".//p")

    grpinsert = "INSERT INTO dbGroup (userid, members) VALUES (?, ?)"
    msginsert = "INSERT INTO dbMessage (groupid, author, time, content) VALUES (?,?,?,?)"

    def simpleCheck(self, file_content, lang):
        logging.info("initial parse check lang: {}".format(lang))

        parser = etree.HTMLParser(encoding='UTF-8')
        root = etree.parse(StringIO(file_content), parser)

        # process group
        content = self.xpathContent(root)[0]

        # start processing
        thread = self.xpathThread(content)[0]
        timetext = self.xpathTime(thread)[0]
        timetext = timetext.strip().rsplit(" ", 1)[0]
        msgtime = datetime.datetime.strptime(timetext, REdict[lang]["parseStr"])

    def parse(self, lang, userid):
        logging.info("user_id: {}, lang: {}".format(userid, lang))

        # get upload data
        db = sqlite3.connect("user.db")
        c = db.cursor()
        c.execute("SELECT file FROM dbUser WHERE id == %d" % (userid))
        data = c.fetchone()
        s = data[0]

        # prepare parser
        parser = etree.HTMLParser(encoding='UTF-8')
        root = etree.parse(StringIO(s), parser)
        content = self.xpathContent(root)[0]
        print(content.text)
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
                c.execute(self.grpinsert, (userid, members))
                groupid = c.lastrowid
                grouplist[members] = groupid
                db.commit()

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

                text = text.text or ""

                msgbuf[idx] = (groupid, author, msgtime, text)

                idx = idx + 1
                if idx == 512:
                    idx = 0
                    c.executemany(self.msginsert, msgbuf)
                    db.commit()

            processed = processed + 1

        if idx != 0:
            c.executemany(self.msginsert, msgbuf[:idx])

        # process end
        endtime = time.time()
        print("Process end, time consumed: {}".format(endtime-starttime))

        # update user info
        c = db.cursor()
        c.execute("UPDATE dbUser SET isReady = 1 WHERE id == %d" % (userid))
        db.commit()

        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit()

    lang = sys.argv[1]
    userid = int(sys.argv[2])

    handler = ParseHandler()
    handler.parse(lang, userid)

