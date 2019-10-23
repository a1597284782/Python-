# -*- coding: utf-8 -*-
import scrapy
import re


class SuningSpider(scrapy.Spider):
    name = 'suning'
    allowed_domains = ['suning.com']
    start_urls = ['https://book.suning.com/']

    def parse(self, response):
        # 获取大分类分组
        div_list = response.css('.menu-item')
        div_sub_list = response.css('.menu-sub')
        for div in div_list[:1]:
            item = {}
            # 大分类名字
            item['b_cate'] = div.css('h3 a::text').get()
            # 获取当前分类的所有中间分类位置
            current_sub_div = div_sub_list[div_list.index(div)]
            # 获取中间分类的分组
            p_list = current_sub_div.css('.submenu-left .submenu-item')
            for p in p_list[:1]:
                # 中间分组名字
                item['m_cate'] = p.css('a::text').get()
                # 获取小分类的分组
                li_list = p.css('.submenu-item + ul li')
                for li in li_list[:1]:
                    # 小分类的名字
                    item['s_cate'] = li.css('li a::text').getall()
                    # 小分类的url
                    item['s_href'] = li.css('li a::attr(href)').get()
                    # print(item)

                    # 请求图书列表页
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_book_list,
                        meta={'item': item}
                    )

                    # 发送请求获取另一半的图书数据
                    next_part_url_temp = 'https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp=0&il=0&iy=0&adNumber=0&n=1&ch=4&prune=0&sesab=ACBAABC&id=IDENTIFYING&cc=535&paging=1&sub=0'
                    # 获取url地址ci
                    ci = item['s_href'].split('-')[1]
                    next_part_url = next_part_url_temp.format(ci)
                    yield scrapy.Request(
                        next_part_url,
                        callback=self.parse_book_list,
                        meta={'item': item}
                    )



    def parse_book_list(self, response):    #处理图书列表页
        item = response.meta['item']
        # 获取图书列表的分组
        # li_list = response.css('.filter-results ul li')
        li_list = response.css('li.product')
        # li_list = response.xpath('//li[contains(@class,"product         book")]')
        print(len(li_list))
        for li in li_list:
            # 书名
            item['book_name'] = li.css('.sell-point a::text').get().strip()
            # 书的url
            item['book_href'] = li.css('.sell-point a::attr(href)').get()
            # 书店名
            item['book_store_name'] = li.css('.seller a::text').get()
            print(item)

        # 翻页
        # 前半部分
        next_url_1 = 'https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp={}&il=0&iy=0&adNumber=0&n=1&ch=4&prune=0&sesab=ACBAABC&id=IDENTIFYING&cc=535'
        # 后半部分
        next_url_2 = 'https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp={}&il=0&iy=0&adNumber=0&n=1&ch=4&prune=0&sesab=ACBAABC&id=IDENTIFYING&cc=535&paging=1&sub=0'
        ci = item['s_href'].split('-')[1]
        # 当前页码数
        current_page = re.findall('param.currentPage = "(.*?)";', response.body.decode())[0]
        # 总的页码数
        total_pase = re.findall('param.pageNumbers = "(.*?)";', response.body.decode())[0]
        if int(current_page) < int(total_pase):
            next_page_num = int(current_page) + 1
            next_url_1 = next_url_1.format(ci, next_page_num)
            yield scrapy.Request(
                next_url_1,
                callback=self.parse_book_list,
                meta={'item': item}
            )
            # 构造后半部分的请求
            next_url_2 = next_url_2.format(ci, next_page_num)
            yield scrapy.Request(
                next_url_2,
                callback=self.parse_book_list,
                meta={'item': item}
            )


            '''
            yield response.follow(
                item['book_href'],
                callback=self.parse_book_detail,
                meta={'item': item}
            )

    def parse_book_detail(self, response):  #处理图书详情页内容
        item = response.meta['item']
        item_url = 'https://pas.suning.com/nspcsale_0_000000011263439015_000000011263439015_0070167435_120_535_5350101_502282_1000234_9231_11796_Z001___R9011205_0.2___.html'
'''
