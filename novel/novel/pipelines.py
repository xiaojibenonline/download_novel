# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import shutil
import re


class NovelPipeline(object):

    def process_item(self, item, spider):
        self.novel_path = item['novel_path']
        self.novel_name = item['novel_name']
        self.chapter_index = item['chapter_index']
        self.chapter_title = item['chapter_title']
        self.chapter_text = item['chapter_text']
        chapter_path = self.novel_path + '/' + self.novel_name + '/' + self.chapter_index + '.txt'
        chapter = self.chapter_title + '\n' + '*' * 20 + '\n' + self.chapter_text + '\n' + '*' * 20 + '\n'
        with open(chapter_path, 'w') as f:
            f.write(chapter)
        return item

    def close_spider(self, spider):
        """
        爬虫完成后合并章节并删除中间文件夹
        :param spider:
        :return:
        """
        copy_path = self.novel_path + '/' + self.novel_name + '/*.txt ' + \
                    self.novel_path + '/' + self.novel_name + '.txt'

        # window下copy /b 后面只能用\
        copy_path = 'copy /b ' + re.sub(r'/', r'\\', copy_path)
        os.system(copy_path)
        shutil.rmtree(self.novel_path + '/' + self.novel_name)
