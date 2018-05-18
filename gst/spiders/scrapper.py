from collections import OrderedDict

import scrapy
import csv
import json

from gst.items import GstItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ['https://www.indiafilings.com/find-gst-rate']

    def parse(self, response):
        # page = response.url.split("/")[-2]
        # filename = 'gst-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
        # Lets find all the chapters in the page. We will use XPath for it
        # XPath for chapter
        chapters = response.xpath('//*[@id="About33"]/div/div/div')
        data = []
        i = 1
        for chapter in chapters:
            # print chapter.xpath('h5/text()').extract()[0]
            i=i+1
            yield scrapy.FormRequest(url="https://www.indiafilings.com/goods.php",
                                          formdata={'attribute': chapter.xpath('h5/@data-goods').extract()[0]},
                                          callback=self.parse_chapter_page,dont_filter = True,meta={
                                                                                  'chapter_name': chapter.xpath('h5/text()').extract()[0]})
                    
       
    #     # for testing-----------------    
            # try:
            #     print chapter.xpath('h5/text()').extract()[0]
            #     yield scrapy.FormRequest(url="https://www.indiafilings.com/goods.php",
            #                               formdata={'attribute': 'Pulp of wood or of other fibrous cellulosic material'},callback=self.parse_chapter_page,
            #                             dont_filter = True,meta={ 'chapter_name': 'Pulp of wood or of other fibrous cellulosic material'})
            # except:
            #     print "in exceptionnnnnnnnnnnnnnnnnnnnn"
            #     print chapter.xpath('h5/text()').extract()[0]
    #                                                                     
    #     # yield scrapy.FormRequest(url="https://www.indiafilings.com/goods.php",
    #     #                                   formdata={'attribute':'Cork and articles of cork'},
    #     #                                   callback=self.parse_chapter_page,dont_filter = True, meta={'chapter_name': 'Cork and articles of cork'})
          
    def parse_chapter_page(self, response):
      
        # self.log("aaaaaaaaaaaaaaaaaaaaaaaaaaaa {}".format(response))
        """
            Data Structure for Chapter
            1	Live Animals	LIVE HORSES, ASSES, MULES AND HINNIES	Horses	Pure-bred breeding animals	HSN 0101 21 00
            data =[{
            "number": 1,
            "chapter_name": "Live Animals",
            "sub_chapter_name": "LIVE HORSES, ASSES, MULES AND HINNIES",
            "category_name": "Horses",
            "sub_category_name": "Pure-bred breeding animals",
            "hsn": "0101 21 00"
        }]
        :param response:
        :return:
        """
        # number = response.meta["number"]
        chapter_name = response.meta["chapter_name"]
        table_rows = response.xpath('/html/body/div/table/tbody')
        category_name = ''
        sub_chapter_name = ''
        sub_category_name = ''
        hsn = ''
        print table_rows
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
           
            # //sanjana-----
            re = scrapy.FormRequest(url="https://www.indiafilings.com/get-description.php",
                                formdata={'query': sub_category_name, 'section': 'Goods'},
                                callback=self.parse_rate,dont_filter = True, meta={'chapter_name':chapter_name, 'sub_chapter_name':sub_chapter_name,
                             'category_name':category_name, 'sub_category_name':sub_category_name, 'hsn':hsn
                                                                })
            print "subbbbb----cat----names ----------"+sub_category_name
            yield re


    def parse_rate(self,response):
        if response.body:
            print response.body
            self.log("ressssssssssssssssssssssssss {}".format(response.body))
            print response.meta["sub_category_name"]
            rateArr = json.loads(response.body)
            rate = rateArr[0]['rate']
            # number=response.meta["number"],
            chapter_name=response.meta["chapter_name"], 
            sub_chapter_name=response.meta["sub_chapter_name"],
            category_name=response.meta["category_name"], 
            sub_category_name=response.meta["sub_category_name"], 
            hsn=response.meta["hsn"]
            # yield GstItem(chapter_name=chapter_name)

            yield GstItem(chapter_name=chapter_name, sub_chapter_name=sub_chapter_name,
                             category_name=category_name, sub_category_name=sub_category_name, hsn=hsn,rate=rate)
        else:
            print "iiiiiinnnnnn ellllssseeee"
            chapter_name=response.meta["chapter_name"], 
            sub_chapter_name=response.meta["sub_chapter_name"],
            category_name=response.meta["category_name"], 
            sub_category_name=response.meta["sub_category_name"], 
            hsn=response.meta["hsn"]
            yield GstItem(chapter_name=chapter_name, sub_chapter_name=sub_chapter_name,
                    category_name=category_name, sub_category_name=sub_category_name, hsn=hsn)
        
            
