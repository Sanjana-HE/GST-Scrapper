from collections import OrderedDict
import scrapy
import csv
import json
from gst.items import GstItem


class QuotesSpider(scrapy.Spider):
    # name of crawler
    name = "quotes"
    # url of site to be crawled
    start_urls = ['https://www.indiafilings.com/find-gst-rate']

    # parse each of chapters obtained
    # make request to each of the chapters to get corresponding data
    def parse(self, response):
        # XPath for chapter
        chapters = response.xpath('//*[@id="About33"]/div/div/div')
        data = []
        i = 1
        for chapter in chapters:
            i=i+1
            
            yield scrapy.FormRequest(url="https://www.indiafilings.com/goods.php",
                                          formdata={'attribute': chapter.xpath('h5/@data-goods').extract()[0]},
                                          callback=self.parse_chapter_page,dont_filter = True,meta={
                                                                                  'chapter_name': chapter.xpath('h5/text()').extract()[0]})
 
    # parse each of data in each chapter
    def parse_chapter_page(self, response):
          chapter_name = response.meta["chapter_name"]
        table_rows = response.xpath('/html/body/div/table/tbody')
        category_name = ''
        sub_chapter_name = ''
        sub_category_name = ''
        hsn = ''
        # looping through each of rows obtained to seperate different data
        for row in table_rows.xpath('//tr')[1::]:
            temp = row.xpath('td/strong/text()').extract()
            if temp:
                temp_name = temp[0]
                # Check if the name endswith :, then its a category name
                if temp_name.rstrip().endswith(':'):
                    category_name = temp_name
                else:
                    try:
                        row.xpath('td[2]/text()').extract()[0]
                    except:
                        category_name = temp_name
                if temp_name.isupper():
                    sub_chapter_name = temp_name
                    category_name = ''                
                continue
            sub_category_name = row.xpath('td[1]/text()').extract()[0]
            hsn = row.xpath('td[2]/text()').extract()[0] 
           # making request to find gst rate for each view button
            re = scrapy.FormRequest(url="https://www.indiafilings.com/get-description.php",
                                formdata={'query': sub_category_name, 'section': 'Goods'},
                                callback=self.parse_rate,dont_filter = True, meta={'chapter_name':chapter_name, 'sub_chapter_name':sub_chapter_name,
                             'category_name':category_name, 'sub_category_name':sub_category_name, 'hsn':hsn
                                                                })
            yield re

    # function to get gst rates and yield it to csv file
    def parse_rate(self,response):
        if response.body:
            rateArr = json.loads(response.body)
            rate = rateArr[0]['rate']
            chapter_name=response.meta["chapter_name"], 
            sub_chapter_name=response.meta["sub_chapter_name"],
            category_name=response.meta["category_name"], 
            sub_category_name=response.meta["sub_category_name"], 
            hsn=response.meta["hsn"]

            yield GstItem(chapter_name=chapter_name, sub_chapter_name=sub_chapter_name,
                             category_name=category_name, sub_category_name=sub_category_name, hsn=hsn,rate=rate)
        else:
            chapter_name=response.meta["chapter_name"], 
            sub_chapter_name=response.meta["sub_chapter_name"],
            category_name=response.meta["category_name"], 
            sub_category_name=response.meta["sub_category_name"], 
            hsn=response.meta["hsn"]
            yield GstItem(chapter_name=chapter_name, sub_chapter_name=sub_chapter_name,
                    category_name=category_name, sub_category_name=sub_category_name, hsn=hsn)
        
            
