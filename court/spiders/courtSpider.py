# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import scrapy.cmdline
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
# from court import CourtItem


# import codecs
# from lxml import etree


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
        # self.driver.set_page_load_timeout(10)

        # self.driver.get("http://wenshu.court.gov.cn/content/content?DocID=b5e21533-e18c-4da7-b642-ca9b1a11a1a3&KeyWord=%E5%9B%9B%E5%B7%9D%E5%BE%B7%E8%83%9C%E9%9B%86%E5%9B%A2%E9%92%92%E9%92%9B%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8")

        # options = webdriver.ChromeOptions()
        # options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        # self.driver = webdriver.Chrome(chrome_options=options,executable_path='D:\program\chromedriver_win32\chromedriver.exe')

    name = "court"
    allowed_domains = ["wenshu.court.gov.cn"]
    start_urls = [
        "http://wenshu.court.gov.cn/Index"
        # "http://wenshu.court.gov.cn/content/content?DocID=b5e21533-e18c-4da7-b642-ca9b1a11a1a3&KeyWord=%E5%9B%9B%E5%B7%9D%E5%BE%B7%E8%83%9C%E9%9B%86%E5%9B%A2%E9%92%92%E9%92%9B%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8"
        # "http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+QWJS+++%E5%85%A8%E6%96%87%E6%A3%80%E7%B4%A2:%E5%86%85%E8%92%99%E5%8F%A4%E5%90%9B%E6%AD%A3%E5%8C%96%E5%B7%A5%E6%9C%89%E9%99%90%E8%B4%A3%E4%BB%BB%E5%85%AC%E5%8F%B8"
   # "http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+QWJS+++%E5%85%A8%E6%96%87%E6%A3%80%E7%B4%A2:%E5%B1%B1%E8%A5%BF%E7%A6%84%E7%BA%AC%E5%A0%A1%E5%A4%AA%E9%92%A2%E8%80%90%E7%81%AB%E6%9D%90%E6%96%99%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8"
   ]

    def parse(self, response):
        self.driver.get(response.url)
        wait = WebDriverWait(self.driver, 5)
        wait.until(lambda driver: driver.find_element_by_id("pageNumber"))  # 列表页内容加载完成后爬取

        self.driver.find_element_by_xpath('//*[@id="gover_search_key"]').clear()
        self.driver.find_element_by_xpath('//*[@id="gover_search_key"]').send_keys(u'四川德胜集团钒钛有限公司')

        span = self.driver.find_element_by_xpath('//*[@id="pageNumber"]/span[2]')
        classValue = span.get_attribute("class")

        # items = []

        while True:
            # item = CourtItem()
            print('class value = '+classValue)
            # 定位文件名称
            title = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div/table/tbody/tr[1]/td/div/a')
            # item['title'] = [c.encode('utf-8') for c in title]
            for t in title:
                print(t.text)

            # 下载文件 //*[@id="resultList"]/div/div[2]/div[2]/img
            # //*[@id="resultList"]/div/div[2]/div[1]/img[@onclick]
            downloads = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div/div[2]/div[2]/img')
            # item['path'] = [c.encode('utf-8') for c in downloads]
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

        self.driver.close()


if __name__ == '__main__':
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', 'court'])
