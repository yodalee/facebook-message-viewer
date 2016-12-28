# -*- coding: utf-8 -*-

# Add all supported language and their parse string here
# run unittest after add a new language

import unittest
import datetime

REdict = {
    "zh_tw": {
        "parseStr":"%Y年%m月%d日 %H:%M", # 2015年1月18日 23:20 UTC+08
        "showName":"繁體中文"},
    "en": {
        "parseStr":"%A, %B %d, %Y  at %H:%M%p", # Wednesday, October 8, 2014 at 4:26pm UTC+08
        "showName":"English"},
}

exampleStr = {
    "zh_tw": {
        "q":"2015年1月18日 23:20 UTC+08",
        "a":datetime.datetime(2015, 1, 18, 23, 20)
    },
    "en": {
        "q":"Wednesday, October 8, 2014 at 4:26pm UTC+08",
        "a":datetime.datetime(2014, 10, 8, 4, 26),
},
}

class REdictParseTest(unittest.TestCase):
    pass

def testParseGen(k, v):
    def test(self):
        timetext = exampleStr[k]["q"].rsplit(" ", 1)[0]
        parse = datetime.datetime.strptime(timetext, v["parseStr"])
        ans = exampleStr[k]["a"]
        assert(ans == parse)
    return test

if __name__ == "__main__":
    for k,v in REdict.items():
        test_func = testParseGen(k, v)
        setattr(REdictParseTest, "test_%s" % (k), test_func)
    unittest.main()
