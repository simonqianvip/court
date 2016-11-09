# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import scrapy.cmdline
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import logging
from court.items import CourtItem
import random


# import codecs
# from lxml import etree
logger = logging.getLogger(__name__)


class CourtSpider(scrapy.Spider):
    def __init__(self):
        # 实例化一个火狐配置对象
        pf = webdriver.FirefoxProfile()
        # 设置成0代表下载到浏览器默认下载路径；设置成2则可以保存到指定目录
        pf.set_preference("browser.download.folderList", 2)
        # 设置下载路径
        pf.set_preference("browser.download.dir", "d:\\court_Download")
        # 不询问下载路径；后面的参数为要下载页面的Content-type的值
        pf.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
        # pf.set_preference("prefs.converted-to-utf8","true")
        self.driver = webdriver.Firefox(firefox_profile=pf,
                                        executable_path='D:\Program Files\Mozilla Firefox\geckodriver-v0.10.0-win64\geckodriver.exe')

    name = "court"
    allowed_domains = ["wenshu.court.gov.cn"]
    start_urls = [
        "http://wenshu.court.gov.cn/Index"
        # "http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+QWJS+++%E5%85%A8%E6%96%87%E6%A3%80%E7%B4%A2:%E5%86%85%E8%92%99%E5%8F%A4%E5%90%9B%E6%AD%A3%E5%8C%96%E5%B7%A5%E6%9C%89%E9%99%90%E8%B4%A3%E4%BB%BB%E5%85%AC%E5%8F%B8"
   # "http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+QWJS+++%E5%85%A8%E6%96%87%E6%A3%80%E7%B4%A2:%E5%B1%B1%E8%A5%BF%E7%A6%84%E7%BA%AC%E5%A0%A1%E5%A4%AA%E9%92%A2%E8%80%90%E7%81%AB%E6%9D%90%E6%96%99%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8"
   ]

    def parse(self, response):
        self.driver.get(response.url)

        self.driver.find_element_by_xpath('//*[@id="gover_search_key"]').clear()
        # TODO 在查询第二个企业的时候必须触发此操作
        # self.driver.find_element_by_xpath('//*[@id="conditionCollect"]/ul/li[3]/a').click()
        # TODO 读取企业库，获取所有的企业名称，待完成
        self.driver.find_element_by_xpath('//*[@id="gover_search_key"]').send_keys(u'四川德胜集团钒钛有限公司')

        self.driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[3]/button').click()

        # wait = WebDriverWait(self.driver, 5)
        # wait.until(lambda driver: driver.find_element_by_id("pageNumber"))  # 列表页内容加载完成后爬取
        try:
            items = []
            flag = True
            page_num = 1
            while flag:
                logger.info('------当前第%d页------'%page_num)
                # TODO 等待下一个页面的元素检查完毕
                wait = WebDriverWait(self.driver, 5)
                wait.until(lambda driver: driver.find_element_by_id("resultList"))

                dataItems = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div')
                if dataItems:
                    # 循环取出当前页面的数据
                    for i in range(1,dataItems.__len__()+1):
                        # 裁判标题
                        title_tags = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%s]/table/tbody/tr[1]/td/div/a'%i)
                        # 法院、编号、日期
                        title_info_tages = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%s]/table/tbody/tr[2]/td/div'%i)
                        # 下载
                        download_tags = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%s]/div[2]/div[2]/img'%i)
                        # 链接
                        link = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%s]/table/tbody/tr[1]/td/div/a'%i)

                        title_text = ''
                        c_name = ''
                        number = ''
                        c_date = ''
                        link = ''

                        if download_tags:
                            for download_link in download_tags:
                                # download_link.click()
                                pass
                        for t in title_tags:
                            title_text = t.text

                        for ti in title_info_tages:
                            info = ti.text
                            words = info.split("   ")
                            if words:
                                c_name = words[0]
                                number = words[1]
                                c_date = words[2]
                        for li in link:
                            url = li.get_attribute('href')
                            link = url
                        '''
                        title = scrapy.Field()
                        c_name = scrapy.Field()
                        number = scrapy.Field()
                        c_date = scrapy.Field()
                        link = scrapy.Field()
                        '''
                        item = CourtItem()
                        item['title'] = title_text
                        item['c_name'] = c_name
                        item['number'] = number
                        item['c_date'] = c_date
                        item['link'] = link
                        items.append(item)
                        print item

                    # 判断进入下一页
                    # span = self.driver.find_element_by_xpath('//*[@id="pageNumber"]/span[2]')
                    # classValue = span.get_attribute("class")

                    span = self.driver.find_elements_by_xpath('//*[@id="pageNumber"]/span')
                    if span.__len__() > 1:
                        classValue = span[1].get_attribute("class")
                    else:
                        classValue = span[0].get_attribute("class")
                    if classValue =="current":
                        aText = self.driver.find_elements_by_xpath('//*[@id="pageNumber"]/a')
                        for a in aText:
                            if a.get_attribute("class") == "next":
                                logger.info("class == " + a.get_attribute("class"))
                                # 点击下一页
                                logger.info('------点击下一页------')
                                a.click()
                                page_num = page_num + 1
                    else:
                        flag = False

                    time.sleep(random(1,10))
        except Exception,e:
            logger.info(e)
        finally:
            self.driver.close()

        print items
        return items

'''
            title = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div/table/tbody/tr[1]/td/div/a')
            for t in title:
                print(t.text)

            downloads = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div/div[2]/div[2]/img')
            for d in downloads:
                print('点击下载……')
                time.sleep(10)
                d.click()

            if classValue =="current":
                aText = self.driver.find_elements_by_xpath('//*[@id="pageNumber"]/a')
                for a in aText:
                    if a.get_attribute("class") == "next":
                        print("class == " + a.get_attribute("class"))
                        # 点击下一页
                        print('点击下一页……')
                        a.click()
                        # TODO 等待下一个页面的元素检查完毕
                        # wait.until(lambda driver: driver.find_element_by_id("resultList"))
                        time.sleep(10)
                        # print(self.driver.get_cookies())
            else:
                break

            span = self.driver.find_elements_by_xpath('//*[@id="pageNumber"]/span')
            if span.__len__() > 1:
                classValue = span[1].get_attribute("class")
            else:
                classValue = span[0].get_attribute("class")
'''



if __name__ == '__main__':
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', 'court'])
