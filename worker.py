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
    xpathContent = "//div[@class='contents']"
    xpathThread = ".//div[@class='thread']"
    xpathMessage = ".//div[@class='message']"
    xpathAuthor = ".//span[@class='user']//text()"
    xpathTime = ".//span[@class='meta']//text()"

    def parse(self, lang, userid):
        logging.info("user_id: {}, lang: {}".format(userid, lang))

        db = sqlite3.connect("user.db")
        c = db.cursor()
        c.execute("SELECT file FROM dbUser WHERE id == %d" % (userid))
        data = c.fetchone()
        s = data[0]

        parser = etree.HTMLParser(encoding='UTF-8')
        root = etree.parse(StringIO(s), parser)

        # process group
        content = root.xpath(self.xpathContent)[0]

        # start processing
        threads = content.xpath(self.xpathThread)
        groupnum = len(threads)
        processed = 0

        print("Process start")
        starttime = time.time()

        for thread in threads:
            members = thread.text.strip()

            query = "INSERT INTO dbGroup (userid, members) VALUES (?, ?)"
            c.execute(query, (userid, members))
            groupid = c.lastrowid
            db.commit()

            print("Process id {}: {}, progress {}/{}".format(
                groupid, members, processed, groupnum))

            messages = thread.xpath(self.xpathMessage)
            for meta in messages:
                author = meta.xpath(self.xpathAuthor)[0].strip()
                timetext = meta.xpath(self.xpathTime)[0].strip()
                # cut down last string "UTC+08"
                # which cause dateparser failed to parse
                timetext = timetext.rsplit(" ", 1)[0]
                msgtime = datetime.datetime.strptime(
                        timetext, REdict[lang]["parseStr"])
                text = meta.getnext().text.strip()

                msgquery = "INSERT INTO dbMessage (groupid, author, time, content) VALUES (?,?,?,?)"

                c.execute(msgquery, (groupid, author, msgtime, text, ))
                db.commit()

            processed = processed + 1

        # # update user info
        endtime = time.time()
        print("Process end, time consumed: {}".format(endtime-starttime))

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

