# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader


class ThingiverseProItem(scrapy.Item):
    num_thing = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    container_id = scrapy.Field()
    comm = scrapy.Field()
    like = scrapy.Field()
    date_thing = scrapy.Field()
    license = scrapy.Field()
    desc_title = scrapy.Field()
    desc_cont = scrapy.Field()
    remixes = scrapy.Field()
    makes = scrapy.Field()
    downloads = scrapy.Field()
    views = scrapy.Field()

class MainItemLoader(ItemLoader):
    default_item_class = ThingiverseProItem


class CommentsItem(scrapy.Item):
    id_container = scrapy.Field()
    comm_content = scrapy.Field()
    papa_id = scrapy.Field()
    comm_author = scrapy.Field()
    comm_date = scrapy.Field()


class CommLoader(ItemLoader):
    default_item_class = CommentsItem




