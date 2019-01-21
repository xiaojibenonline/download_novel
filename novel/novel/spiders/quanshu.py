# -*- coding: utf-8 -*-
"""
根据输入的关键词下载小说
"""
import scrapy
from ..items import NovelItem
from urllib import parse
import re
import os
from tkinter.filedialog import askdirectory
import tkinter

os.system('scrap crawl quanshu')


class QuanshuSpider(scrapy.Spider):
    name = 'quanshu'  # 爬虫名字，唯一
    allowed_domains = ['www.quanshuwang.com']
    search_url = 'http://www.quanshuwang.com/modules/article/search.php?searchkey={}'\
        .format(parse.quote(input('请输入需要下载的小说:'), encoding='gbk'))
    start_urls = [search_url]  # 初始列表

    def parse(self, response):
        """
        根据关键词返回所有相关小说，选择需要的下载
        :param response:
        :return:
        """

        # 获取小说大纲总页数
        all_pages = response.xpath('//em[@id="pagestats"]/text()').extract_first()
        page_num = re.findall(r'/(\d*)', all_pages)[0]

        # 创建当前页小说序号字典
        next_links = dict()

        # 获取当前页小说信息
        novels_info = response.xpath('//ul[@class="seeWell cf"]/li')

        # 遍历将所有小说信息存入字典
        for index, novel_info in enumerate(novels_info):
            novel_name = novel_info.xpath('./span/a/@title').extract_first()
            novel_name = re.sub(r'？', '?', novel_name)  # 避免中文字符出错
            novel_auth = novel_info.xpath('./span/a[2]/text()').extract_first()
            novel_link = novel_info.xpath('./a/@href').extract_first()
            true_novel_link = re.sub(r'_', r'/0/', novel_link).split('.html')[0]
            next_links.setdefault(index + 1, [true_novel_link, novel_name])
            print('序号{}>> {} 作者：{}'.format(index + 1, novel_name, novel_auth))

        # 选择需要下载的小说
        choice = int(input('请按照序号选择,输入0选择其他页面:'))
        if choice == 0:
            page = input('请输入页码1-{}：'.format(page_num))
            return scrapy.Request(url=response.url + '&page={}'.format(page))
        chose_novel_link = next_links[choice][0]
        chose_novel_name = next_links[choice][1]

        # 调用novel_parse
        return scrapy.Request(url=chose_novel_link, callback=self.novel_parse,
                              meta={'chose_novel_name': chose_novel_name})

    def novel_parse(self, response):
        """
        根据小说链接返回章节链接
        :param response:
        :return:
        """

        # 获取小说名称、章节及章节链接
        novel_name = response.meta['chose_novel_name']
        chapter_titles = response.xpath('//div[@class="clearfix dirconone"]/li/a/text()').extract()
        chapter_links = response.xpath('//div[@class="clearfix dirconone"]/li/a/@href').extract()
        chapter_indexes = range(1, len(chapter_titles) + 1)

        # 选择小说文件夹
        print('请选择下载路径：')
        root = tkinter.Tk()
        path = askdirectory(parent=root, title='请选择下载路径')
        root.destroy()
        os.mkdir(path + '/' + novel_name)

        # 传入小说下载地址、名称、章节及章节链接
        for chapter_title, chapter_link, chapter_index in zip(chapter_titles, chapter_links, chapter_indexes):
            yield scrapy.Request(url=chapter_link, callback=self.chapter_parse,
                                 meta={'novel_path': path, 'novel_name': novel_name,
                                       'chapter_title': chapter_title, 'chapter_index': chapter_index})

    def chapter_parse(self, response):
        """
        根据小说章节链接爬取内容
        :param response:
        :return:
        """

        # 保存失败章节
        if response.status != 200:
            self.logger('{}{}{}'.format(response.url, response.meta['novel_name'], response.meta['chapter_title']))

        chapter_title = response.meta['chapter_title']
        chapter_index = str(response.meta['chapter_index'])
        while len(chapter_index) < 6:
            chapter_index = '0' + chapter_index

        # 获取章节内容
        chapter_all_text = response.xpath('//div[@id="content"]/text()').extract()
        chapter_text = ''.join(chapter_all_text)

        # 替换\xa0为空格，避免保存编码问题
        real_chapter_text = re.sub(r'\xa0', r' ', chapter_text)

        # 获取章节下载地址,保存章节内容
        # novel_path = response.meta['novel_path']
        # novel_name = response.meta['novel_name']
        # chapter_path = novel_path + '/' + novel_name + '/' + chapter_index + '.txt'
        # with open(chapter_path, 'w', encoding='gbk') as f:
        #     f.write(chapter_title + '\n' + '*' * 20 + '\n' + real_chapter_text + '*' * 20 + '\n')
        item = NovelItem()
        item['novel_path'] = response.meta['novel_path']
        item['novel_name'] = response.meta['novel_name']
        item['chapter_index'] = chapter_index
        item['chapter_title'] = chapter_title
        item['chapter_text'] = real_chapter_text
        yield item
