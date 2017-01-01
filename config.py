# -*- coding: utf-8 -*-

# Add all supported language and their parse string here
# run unittest after add a new language

import datetime

REdict = {
    "zh_tw": {
        "parseStr":"%Y年%m月%d日 %H:%M", # 2015年1月18日 23:20 UTC+08
        "showName":"繁體中文"},
    "en": {
        "parseStr":"%A, %B %d, %Y  at %H:%M%p", # Wednesday, October 8, 2014 at 4:26pm UTC+08
        "showName":"English"},
}

REdictTest = {
    "zh_tw": {
        "q":"2015年1月18日 23:20 UTC+08",
        "a":datetime.datetime(2015, 1, 18, 23, 20)
    },
    "en": {
        "q":"Wednesday, October 8, 2014 at 4:26pm UTC+08",
        "a":datetime.datetime(2014, 10, 8, 4, 26),
    },
}

