# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
import webapp2

import time
import logging
from lxml import etree
import sys
import datetime

from dbmodel import dbUser, dbGroup, dbMessage

reload(sys)
sys.setdefaultencoding("utf-8")


class ParseHandler(blobstore_handlers.BlobstoreDownloadHandler):
    xpathContent = "//div[@class='contents']"
    xpathThread = ".//div[@class='thread']"
    xpathMessage = ".//div[@class='message']"
    xpathAuthor = ".//span[@class='user']//text()"
    xpathTime = ".//span[@class='meta']//text()"

    REdict = {
        "zh_tw": "%Y年%m月%d日 %H:%M" # 2015年1月18日 23:20 UTC+08
    }

    @ndb.toplevel
    def post(self):
        blob_key = self.request.get('blob_key')
        url_str = self.request.get('user_key')
        lang = self.request.get('lang')
        logging.info("blob_key: {}, user_key: {}, lang: {}".format(
            blob_key, url_str, lang))

        user_key = ndb.Key(urlsafe=url_str)
        # fetch the blob

        blob_reader = blobstore.BlobReader(blob_key)
        parser = etree.HTMLParser(encoding='UTF-8')
        root = etree.parse(blob_reader, parser)

        # process group
        content = root.xpath(self.xpathContent)[0]

        # start processing
        threads = content.xpath(self.xpathThread)
        processed = 0
        msgbuf = [None] * 512

        print("Process start")
        starttime = time.time()

        for thread in threads:
            members = thread.text.strip()
            print("Process: {}, progress {}/{}".format(members, processed, len(threads)))
            group = dbGroup(
                user_key = user_key,
                group = members)

            group_key = group.put()

            messages = thread.xpath(self.xpathMessage)
            remain = len(messages) & 0x1ff
            for i,meta in enumerate(messages):
                author = meta.xpath(self.xpathAuthor)[0].strip()
                timetext = meta.xpath(self.xpathTime)[0].strip()
                # cut down last string "UTC+08"
                # which cause dateparser failed to parse
                timetext = timetext.rsplit(" ", 1)[0]
                msgtime = datetime.datetime.strptime(timetext, self.REdict[lang])
                text = meta.getnext().text.strip()

                msgbuf[i&0x1ff] = dbMessage(
                    group_key = group_key,
                    author = author,
                    time = msgtime,
                    content = text)

                if i == 511:
                    ndb.put_multi_async(msgbuf)

            if remain != 0:
                ndb.put_multi_async(msgbuf[:remain])

            processed = processed + 1

        # update user info
        endtime = time.time()
        print("Process end, time consumed: {}".format(endtime-starttime))

        userdata = user_key.get()
        userdata.isReady = True
        userdata.put()


app = webapp2.WSGIApplication([
    ('/parse', ParseHandler)
    ], debug=True)

