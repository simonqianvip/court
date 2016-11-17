# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CourtItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    c_name = scrapy.Field()
    number = scrapy.Field()
    c_date = scrapy.Field()
    link = scrapy.Field()
    # 原告
    prosecutor = scrapy.Field()
    # prosecutor_name = scrapy.Field()
    # 被告
    accused = scrapy.Field()
    # accused_name = scrapy.Field()
    # 判决类型
    sentence = scrapy.Field()
    # 企业名称
    search = scrapy.Field()
    pass
