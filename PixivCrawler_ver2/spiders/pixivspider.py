# -*- coding: utf-8 -*-
import random
import os
import scrapy
import re
import numpy as np
import pandas
from pandas import Series, DataFrame
from PixivCrawler_ver2.items import PixivcrawlerVer2Item

# https://www.pixiv.net/artworks/82694815
# https://www.pixiv.net/artworks/83224693

url_list = []
h_origon = []


class PixivspiderSpider(scrapy.Spider):
    name = 'pixivspider'
    start_urls = ['https://accounts.pixiv.net/login']

    def __init__(self):
        super().__init__()
        self.src_list = Series([])

    def jojo_parse(self, response):
        print("+" * 30)
        p_items = {'src': response.xpath('//div[@role="presentation"]/a/@href').getall(), 'referer': response.pri_url}
        tag = response.xpath('//div[@role="presentation"]//div[@aria-label]//text()').get()
        print(tag)
        if tag:
            p_items['index'] = int(tag.replace('1/', ''))
        else:
            p_items['index'] = 1
        print('--------D_SPIDER----------')
        print(p_items['src'])
        n_item = PixivcrawlerVer2Item(srcs=p_items['src'], referer=p_items['referer'], index=p_items['index'])
        yield n_item
        print("+" * 30)

    def dio_parse(self, response):
        print('*' * 30)
        global url_list, h_origon
        url_list.append(response.url)
        origon = []
        pri_items = {}

        pattern = r'/artworks/\d+'
        artworks = response.xpath('//aside//ul/li//a/@href').getall()
        artworks_illust = response.xpath('//div[@type="illust"]//a/@href').getall()
        artworks.extend(artworks_illust)
        pri_items['src'] = response.xpath('//div[@role="presentation"]/a/@href').getall()
        pri_items['referer'] = response.pri_url
        tag = response.xpath('//div[@role="presentation"]//div[@aria-label]//text()').get()

        yield scrapy.Request(response.url, callback=self.jojo_parse, dont_filter=True)

        origon = re.findall(pattern, str(artworks))

        if origon:
            h_origon.extend(origon)
            print(len(h_origon))

        if tag:
            pri_items['index'] = int(tag.replace('1/', ''))
        else:
            pri_items['index'] = 0
        print('--------P_SPIDER----------')
        print(pri_items['src'])

        for ori_url in origon:

            if not self.src_list.empty:
                if self.src_list.str.count(ori_url).sum():
                    print('Url have been crawled before')
                    continue

            mk_url = "https://www.pixiv.net" + ori_url
            yield scrapy.Request(mk_url, callback=self.jojo_parse, dont_filter=False)
        else:
            self.src_list = self.src_list.append(Series(origon), ignore_index=True)
            print('--------P_SPIDER----------')
            print('length of url list in this turn(propagation):\n' + str(len(self.src_list)))

    def parse(self, response):
        print('*' * 30)
        global url_list, h_origon
        url_list.append(response.url)
        origon = []
        pri_items = {}

        pattern = r'/artworks/\d+'
        artworks = response.xpath('//aside//ul/li//a/@href').getall()
        artworks_illust = response.xpath('//div[@type="illust"]//a/@href').getall()
        artworks.extend(artworks_illust)
        pri_items['src'] = response.xpath('//div[@role="presentation"]/a/@href').getall()
        pri_items['referer'] = response.pri_url
        tag = response.xpath('//div[@role="presentation"]//div[@aria-label]//text()').get()

        yield scrapy.Request(response.url, callback=self.jojo_parse, dont_filter=True)

        origon = re.findall(pattern, str(artworks))


        if origon:
            h_origon.extend(origon)
            print(len(h_origon))

        if tag:
            pri_items['index'] = int(tag.replace('1/', ''))
        else:
            pri_items['index'] = 0
        print('--------SPIDER----------')
        print(pri_items['src'])

        # fir_item = PixivcrawlerVer2Item(srcs=pri_items['src'], referer=pri_items['referer'], index=pri_items['index'])

        for ori_url in origon:

            if not self.src_list.empty:
                if self.src_list.str.count(ori_url).sum():
                    print('Url have been crawled before')
                    continue

            mk_url = "https://www.pixiv.net" + ori_url
            yield scrapy.Request(mk_url, callback=self.dio_parse, dont_filter=False)
        else:
            self.src_list = self.src_list.append(Series(origon), ignore_index=True)
            print('--------SPIDER----------')
            print('length of url list in this turn:\n' + str(len(self.src_list)))
            ori_url = h_origon[random.randrange(len(h_origon))]
            mk_url = "https://www.pixiv.net" + ori_url

            yield scrapy.Request(mk_url, callback=self.parse, dont_filter=True)


