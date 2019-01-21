# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 小说信息
    novel_path = scrapy.Field()
    novel_name = scrapy.Field()
    chapter_index = scrapy.Field()
    chapter_title = scrapy.Field()
    chapter_text = scrapy.Field()
