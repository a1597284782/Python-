# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com', 'p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):  # 提取所有的大分类和对应的小分类
        dt_list = response.css('.mc dl dt')
        for dt in dt_list:
            item = {}
            # 大分类
            item['b_cate'] = dt.css('a::text').get()
            # 获取小分类的分组
            em_list = dt.css('dt + dd em')
            for em in em_list:
                # 小分类的名字
                item['s_cate'] = em.css('a::text').get()
                # 小分类的地址
                item['s_href'] = 'https:' + em.css('a::attr(href)').get()
                # 构造小分类url地址请求，进入列表页
                yield scrapy.Request(
                    item['s_href'],
                    callback=self.parse_book_list,
                    meta={'item': deepcopy(item)}
                )

    def parse_book_list(self, response):    # 提取图书信息
        item = response.meta['item']
        # 图书列表页分组
        li_list = response.css('ul.gl-warp.clearfix .gl-item')
        for li in li_list:
            item['book_name'] = li.css('.p-name a em::text').get().strip()
            item['book_author'] = li.css('.p-bi-name .author_type_1 a::text').get()
            item['book_press'] = li.css('.p-bi-store a::text').get()
            item['book_date'] = li.css('.p-bi-date::text').get().strip()
            item['book_sku'] = li.css('div::attr(data-sku)').get()
            # 发送价格请求，获取价格
            price_url_temp = 'https://p.3.cn/prices/mgets?&ext=11101100&pin=&type=1&area=13_1042_3126_0&skuIds=J_{}'
            price_url = price_url_temp.format(item['book_sku'])
            yield scrapy.Request(
                price_url,
                callback=self.parse_book_price,
                meta={'item': deepcopy(item)}
            )

            # 图书列表翻页
            next_url = response.css('.pn-next::attr(href)').get()
            if next_url is not None:
                yield response.follow(
                    next_url,
                    callback=self.parse_book_list,
                    meta={'item': deepcopy(item)}
                )

    def parse_book_price(self, response):   # 提取图书价格
        item = response.meta['item']
        item['book_price'] = json.loads(response.body.decode())[0]['op']
        print(item)
