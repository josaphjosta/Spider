# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PixivcrawlerVer2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    srcs = scrapy.Field()
    referer = scrapy.Field()
    index = scrapy.Field()
