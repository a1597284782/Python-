# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider


class AmazonSpider(RedisCrawlSpider):
    name = 'amazon'
    allowed_domains = ['amazon.cn']
    # start_urls = ['http://amazon.cn/']
    redis_key = 'amazon'

    rules = (
        # 实现提取大分类的url地址,同时还能提取小分类的url
        Rule(LinkExtractor(restrict_xpaths=('//ul[contains(@class,"a-unordered-list a-nostyle a-vertical s-ref-indent-")]/div/li',)), follow=True),
        # 实现提取图书详情页的url
        Rule(LinkExtractor(restrict_xpaths=('//div[@id="mainResults"]/ul/li//h2/..',)), callback='parse_item'),
        # 实习图书列表翻页(翻页后结构变了，待修改)
        # Rule(LinkExtractor(restrict_xpaths=('//div[@id="pagn"]//a',)), follow=True),
    )

    def parse_item(self, response):
        item = {}
        item['book_cate'] = response.xpath(
            '//div[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[not(@class)]//a/text()').getall()
        item['book_name'] = response.xpath('//span[contains(@id,"ProductTitle")]/text()').get()
        item['book_author'] = response.xpath('//div[@id="bylineInfo"]/span/a/text()').getall()
        item['book_press'] = response.xpath('//b[text()="出版社:"]/../text()').get()
        item['book_url'] = response.url
        item['book_price'] = response.xpath('//span[@class="a-size-medium a-color-price"]/text()').get()
        # item['book_img'] = response.xpath('//div[contains(@id,"img-canvas")]/img/@src').get()

        yield item