# -*- coding= utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in=
# https=//doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GstItem(scrapy.Item):
    # define the fields for your item here like=
    # name = scrapy.Field()
    # number = scrapy.Field()
    chapter_name = scrapy.Field()
    sub_chapter_name = scrapy.Field()
    category_name = scrapy.Field()
    sub_category_name = scrapy.Field()
    hsn = scrapy.Field()
    rate = scrapy.Field()
