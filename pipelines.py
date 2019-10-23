# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re


class DangDangPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'dangdang':
            item['b_cate'] = ''.join([i.strip() for i in item['b_cate']])
            item['m_cate'] = ''.join([i.strip() for i in item['m_cate']])
        return item


class AmazonPipeline(object):
    def process_item(self, item, spider):
        if spider.name =='amazon':
            item['book_name'] = item['book_name'].strip()
            item['book_author'] = [re.sub('&|更多|\s', '', i) for i in item['book_author']]
            item['book_author'] = [i for i in item['book_author'] if(len(str(i)) != 0)]
            item['book_cate'] = [i.strip() for i in item['book_cate']]
            item['book_price'] = item['book_price'].strip()
            # print(item)
        return item