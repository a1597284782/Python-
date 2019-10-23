# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from copy import deepcopy


class DangdangSpider(RedisSpider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    # start_urls = ['http://dangdang.com/']
    redis_key = 'dangdang'

    def parse(self, response):
        # 大分类分组
        div_list = response.css('.con.flq_body .level_one')[1:]
        for div in div_list:
            item = {}
            # 大分类的名字
            item['b_cate'] = div.css('.primary_dl dt ::text').getall()
            # 获取中间分类的分组
            dl_list = div.css('.submenu .eject_left .inner_dl')
            for dl in dl_list:
                # 中间分类的名字
                item['m_cate'] = dl.css('dt a::text').get()
                # 获取小分类的分组
                a_list = dl.css('dd a')
                for a in a_list:
                    # 小分类的名字
                    item['s_cate'] = a.css('a::text').get()
                    # 小分类的url
                    item['s_href'] = a.css('a::attr(href)').get()
                    # 发送请求获得列表页
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_book_list,
                        meta={'item': deepcopy(item)}
                    )

    def parse_book_list(self, response):    # 提取列表页的数据
        item = response.meta['item']
        # 图书分组
        li_list = response.css('#component_59 li')
        for li in li_list:
            item['book_name'] = li.css('a.pic::attr(title)').get()
            item['book_href'] = li.css('a.pic::attr(href)').get()
            item['book_author'] = li.css('p.search_book_author > span:nth-child(1) a::text').getall()
            item['book_press'] = li.css('p.search_book_author > span:nth-child(3) a::text').get()
            item['book_price'] = li.css('p.price > span.search_now_price::text').get()
            yield item

        # 翻页
        next_url = response.css('.paging li.next::attr(href)').get()
        if next_url is not None:
            yield response.follow(
                next_url,
                callback=self.parse_book_list,
                meta={'item': item}
            )
