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
import re
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from court.util.mysql_util import SqlUtil
from autopy import alert
from autopy import mouse
from autopy import key
import autopy

from PIL import Image
import pytesseract

import urllib
from io import BytesIO
from selenium.common.exceptions import *

logger = logging.getLogger(__name__)
# 下载的文件目录
File_DIR = 'd:\\court_Download'
company_name = u'福建海源自动化机械股份有限公司'
'''
濮阳濮耐高温材料（集团）股份有限公司 股票代码：002225 股票简称：濮耐股份
山东鲁阳节能材料股份有限公司 股票代码：002088 股票简称：鲁阳节能
瑞泰科技股份有限公司 股票代码：002066 股票简称：瑞泰科技
北京金隅股份有限公司 股票代码：601992 股票简称：金隅股份
广东东方锆业科技股份有限公司 股票代码：002167 股票简称：东方锆业
福建海源自动化机械股份有限公司 股票代码：002529 股票简称：海源机械
'''


class CourtSpider(scrapy.Spider):
    '''
    1,火狐下载，不能修改文件名称
    2,纯数字的验证码可以破解
    '''
    def __init__(self):
        # 实例化一个火狐配置对象
        # pf = webdriver.FirefoxProfile()
        # # # 设置成0代表下载到浏览器默认下载路径；设置成2则可以保存到指定目录
        # pf.set_preference("browser.download.folderList", 2)
        # # # 设置下载路径
        # pf.set_preference("browser.download.dir", "d:\\court_Download")
        # # # 不询问下载路径；后面的参数为要下载页面的Content-type的值
        # pf.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
        # pf.set_preference("prefs.converted-to-utf8","true")
        # self.driver = webdriver.Firefox(firefox_profile=pf,
        #                                 executable_path='D:\Program Files\Mozilla Firefox\geckodriver-v0.10.0-win64\geckodriver.exe')
        # 连接mysql数据库，并查询论文名称
        self.init_mysql()
        logger.info('init mysql database')
        # TODO alert的捕捉
        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': File_DIR,
                 'CapabilityType':'UNEXPECTED_ALERT_BEHAVIOUR','UnexpectedAlertBehaviour':'ACCEPT'}
        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        # capabilities_chrome = DesiredCapabilities.CHROME
        # DesiredCapabilities dc = new DesiredCapabilities();
        # dc.setCapability(CapabilityType.UNEXPECTED_ALERT_BEHAVIOUR,
        # UnexpectedAlertBehaviour.ACCEPT);
        self.driver = webdriver.Chrome(chrome_options=options,executable_path='D:\program\chromedriver_win32\chromedriver.exe')

    def init_mysql(self):
        '''
        初始化连接mysql数据库
        :return: 连接对象
        '''
        self.mysql_util = SqlUtil('127.0.0.1', 'root', '123456', 'fm')
        self.mysql_util.connect()

    name = "court"
    allowed_domains = ["wenshu.court.gov.cn"]
    start_urls = [
        "http://wenshu.court.gov.cn/Index"
   ]

    def GetNowTime(self):
        '''
        获取当前系统时间
        :return:
        '''
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def parse(self, response):
        # 获取时间
        s_time = self.GetNowTime()

        self.driver.get(response.url)
        # TODO 查询企业
        self.search_company()

        # TODO 用来获取验证码
        self.get_validateCode()

        # TODO　选择每页显示的条数
        self.select_page_number()

        main_handle = self.driver.current_window_handle

        # wait = WebDriverWait(self.driver, 5)
        # wait.until(lambda driver: driver.find_element_by_id("pageNumber"))  # 列表页内容加载完成后爬取
        try:
            items = []
            flag = True
            page_num = 1
            download_count = 0
            while flag:
                logger.info('------当前第%d页------'%page_num)
                # TODO 等待元素的定为
                self.driver.implicitly_wait(15)
                dataItems = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div')

                time.sleep(10)
                logger.info('dataItems.length = %d'%len(dataItems))


                if dataItems:
                    # 循环取出当前页面的数据
                    for i in range(1,len(dataItems)+1):
                        # 裁判标题
                        title_tags = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%s]/table/tbody/tr[1]/td/div/a'%i)
                        # 法院、编号、日期
                        title_info_tages = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%s]/table/tbody/tr[2]/td/div'%i)
                        # 下载
                        download_tags = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%s]/div[2]/div[2]/img'%i)
                        # 链接
                        links = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%s]/table/tbody/tr[1]/td/div/a'%i)

                        title_text = ''
                        c_name = ''
                        number = ''
                        c_date = ''
                        link = ''
                        # 判决书类型
                        sentence = ''
                        # 原告
                        prosecutor = []
                        # 被告
                        accused = []

                        for li in links:
                            url = li.get_attribute('href')
                            link = url

                        # TODO 数据增量更新
                        '''
                        1,判断当前url是否存在
                            存在，详情页都不进入，数据也不保存
                            不存在，则相反
                        '''
                        query_sql = """select * from court_info where link = '%s'""" % link
                        results = self.mysql_util.get_data_from_db(query_sql)
                        if results:
                            logger.info('------------Data is Exist------------')
                        else:
                            if download_tags:
                                for download_link in download_tags:
                                    # TODO 下载裁判文书
                                    download_link.click()
                                    download_count = download_count + 1
                                    # pass
                            for t in title_tags:
                                title_text = t.text

                            for ti in title_info_tages:
                                info = ti.text
                                words = info.split("   ")
                                if words:
                                    c_name = words[0]
                                    number = words[1]
                                    c_date = words[2]


                            a_tags = self.driver.find_elements_by_xpath('//*[@id="resultList"]/div[%d]/table/tbody/tr[1]/td/div/a'%i)
                            for a in a_tags:
                                # 点击标题，打开详情页
                                a.click()

                            handles = self.driver.window_handles
                            # 切换到二级页面
                            for h in handles:
                                if h != main_handle:
                                    self.driver.switch_to_window(h)
                            # 获取判断文书类型
                            sentences = self.driver.find_elements_by_xpath('//*[@id="DivContent"]/div[2]')
                            if sentences:
                                for s in sentences:
                                    sentence = s.text

                            # TODO 上诉人
                            self.get_second_page_info(accused, prosecutor)
                            time.sleep(random.randint(3,5))
                            # 关闭详情页
                            self.close_second_page(main_handle)
                            # 返回到主窗口
                            self.driver.switch_to_window(main_handle)

                            '''
                            title = scrapy.Field()
                            c_name = scrapy.Field()
                            number = scrapy.Field()
                            c_date = scrapy.Field()
                            link = scrapy.Field()
                            # 判决类型
                            sentence = scrapy.Field()
                             # 原告
                            prosecutor = scrapy.Field()
                            # 被告
                            accused = scrapy.Field()
                            '''
                            item = CourtItem()
                            item['title'] = title_text
                            item['c_name'] = c_name
                            item['number'] = number
                            item['c_date'] = c_date
                            item['link'] = link
                            item['sentence'] = sentence
                            up = ''.join(prosecutor)
                            item['prosecutor'] = up.encode('utf-8')
                            ua = ''.join(accused)
                            item['accused'] = ua.encode('utf-8')
                            item['search'] = company_name
                            items.append(item)

                            time.sleep(random.randint(5, 10))

                    flag, page_num = self.next_page(flag, page_num)

            # TODO 爬虫数据更新
            e_time = self.GetNowTime()
            u_count = len(items)
            # 插入更新语句
            insert_sql = """
                    insert into spider_info(site,s_time,e_time,update_count,download_count)
                    values('文书网','%s','%s','%s','%s')"""%(s_time,e_time,u_count,download_count)
            results = self.mysql_util.exec_db_cmd(insert_sql)

            #    等待最后一个文件下载完，再关闭chrome浏览器

            time.sleep(10)
            logger.info('wait download for the last file , sleep 10 s')
        except UnexpectedAlertPresentException:
            # TODO 捕捉警告窗口, 点击确认按钮
            to_alert = self.driver.switch_to.alert
            alert_text = to_alert.text
            logger.info(alert_text)
            to_alert.accept()
        except Exception,e:
            logger.info(e)
        finally:
            # 关闭数据库连接
            self.mysql_util.disconnect()
            self.driver.close()
            logger.info('close webdriver')
        return items

    def next_page(self, flag, page_num):
        '''
        判断进入下一页
        :param flag:
        :param page_num:
        :return:
        '''
        # span = self.driver.find_element_by_xpath('//*[@id="pageNumber"]/span[2]')
        # classValue = span.get_attribute("class")
        # span = self.driver.find_elements_by_xpath('//*[@id="pageNumber"]/span')
        # # 获取当前显示的页数
        # if len(span) > 1:
        #     classValue = span[1].get_attribute("class")
        # else:
        #     classValue = span[0].get_attribute("class")
        #
        # if classValue == "current":
        #     aText = self.driver.find_elements_by_xpath('//*[@id="pageNumber"]/a')
        #     for a in aText:
        #         if a.get_attribute("class") == "next":
        #             logger.info("class == " + a.get_attribute("class"))
        #             # 点击下一页
        #             logger.info('------点击下一页------')
        #             page_num = page_num + 1
        #             flag = True
        #             a.click()
        #         else:
        #             flag = False
        # else:
        #     flag = False
        # TODO 待测试
        a_tags = self.driver.find_elements_by_xpath('//*[@id="pageNumber"]/a')
        if a_tags:
            for a in a_tags:
                a_text = a.text
                if a_text == u'下一页':
                    # 点击下一页
                    logger.info('------点击下一页------')
                    page_num = page_num + 1
                    flag = True
                    a.click()
                else:
                    flag = False
        else:
            flag = False

        rd = random.randint(1, 60)
        time.sleep(rd)
        logger.info('------click next_page is sleep %s s------' % rd)

        return flag, page_num

    def close_second_page(self, main_handle):
        '''
        关闭二级页面
        :param main_handle:
        :return:
        '''
        second_handles = self.driver.window_handles
        for s in second_handles:
            if s != main_handle:
                time.sleep(random.randint(1,5))
                self.driver.switch_to_window(s)
                self.driver.close()

    def get_second_page_info(self, accused, prosecutor):
        '''
        获取二级页面的详情信息
        :param accused:
        :param prosecutor:
        :return:
        '''
        divs = self.driver.find_elements_by_xpath('//*[@id="DivContent"]/div')
        if divs:
            for div in divs:
                div_text = div.text
                splitObj = div_text.split('，')
                strs = splitObj[0]
                matchObj = re.search(u'有限公司', strs, re.I)
                if matchObj:
                    if strs.__contains__('：'):
                        split1 = splitObj[0].split('：')
                        # 获取带有冒号的公司名称
                        # TODO 字符串中必须包含'上诉人（原审原告）'，'被上诉人（原审被告）','上诉人（原审被告）','被上诉人（原审原告）','被告','原告'，否则不能输出
                        if split1[0].__contains__(u'上诉人（原审原告）') or split1[0].__contains__(u'被上诉人（原审被告）') or split1[
                            0].__contains__(u'上诉人（原审原告）') \
                                or split1[0].__contains__(u'被上诉人（原审被告）') or split1[0].__contains__(u'被告') or split1[
                            0].__contains__(u'原告'):
                            # print split1
                            if split1[0].__contains__(u'公司'):
                                logger.info("No Match!!")
                            else:
                                if split1[0].startswith(u'原') or split1[0].startswith(u'上'):
                                    # logger.info(split1[0] + ',' + split1[1])
                                    prosecutor.append(split1[1] + ',')
                                elif split1[0].startswith(u'被'):
                                    # print split1[0] + ',' + split1[1]
                                    accused.append(split1[1] + ',')
                        else:
                            logger.info( "No Match!")
                    else:
                        if strs.__contains__('、'):
                            logger.info( "No Match")
                        else:
                            if strs.__contains__(u'上诉人（原审原告）'):
                                if strs.__contains__(u'被上诉人（原审被告）'):
                                    logger.info('No Match!!')
                                else:
                                    if strs.startswith(u'上诉人（原审原告）'):
                                        prosecutor.append(strs[9:] + ',')
                                        # print strs[0:9] + ',' + strs[9:]

                            elif strs.__contains__(u'被上诉人（原审被告）'):
                                if strs.__contains__(u'上诉人（原审原告）'):
                                    logger.info('No Match!!')
                                else:
                                    if strs.startswith(u'被上诉人（原审被告）'):
                                        accused.append(strs[10:] + ',')
                                        # print strs[10:]

                            elif strs.__contains__(u'上诉人（原审被告）'):
                                if strs.__contains__(u'被上诉人（原审原告）'):
                                    logger.info('No Match!!')
                                else:
                                    if strs.startswith(u'上诉人（原审被告）'):
                                        prosecutor.append(strs[9:] + ',')
                                        # print strs[9:]

                            elif strs.__contains__(u'被上诉人（原审原告）'):
                                if strs.__contains__(u'上诉人（原审被告）'):
                                    logger.info('No Match!!')
                                else:
                                    if strs.startswith(u'被上诉人（原审原告）'):
                                        accused.append(strs[10:] + ',')
                                        # print strs[10:]

                            elif strs.__contains__(u'被告'):
                                if strs.__contains__(u'原告'):
                                    logger.info('No Match!!')
                                else:
                                    if strs.startswith(u'被告'):
                                        accused.append(strs[2:] + ',')
                                        # print strs[2:]

                            elif strs.__contains__(u'原告'):
                                if strs.__contains__(u'被告'):
                                    logger.info('No Match!!')
                                else:
                                    if strs.startswith(u'原告'):
                                        prosecutor.append(strs[2:] + ',')
                            elif strs.__contains__(u'申请执行人'):
                                if strs.__contains__(u'被执行人'):
                                    logger.info('No Match!!')
                                else:
                                    if strs.startswith(u'申请执行人'):
                                        prosecutor.append(strs[5:] + ',')

                            elif strs.__contains__(u'被执行人'):
                                if strs.__contains__(u'申请执行人'):
                                    logger.info('No Match!!')
                                else:
                                    if strs.startswith(u'被执行人'):
                                        accused.append(strs[4:] + ',')
                            else:
                                logger.info("No match!!")
                else:
                    logger.info("No match!!!")

    def get_validateCode(self):
        '''
        破解验证码
        :return:
        '''

        validates = self.driver.find_elements_by_xpath('//*[@id="trValidateCode"]')
        vcode = ''
        if validates:
            imgs = self.driver.find_elements_by_xpath('//*[@id="trValidateCode"]/td[2]/img')
            for img in imgs:
                src = img.get_attribute('src')

                jpg = urllib.urlopen(src)
                jpgFile = jpg.read()
                image = Image.open(BytesIO(jpgFile))
                vcode = pytesseract.image_to_string(image)
                # print 'code = %s' % vcode
            time.sleep(5)
            # 输入验证码
            self.driver.find_element_by_xpath('//*[@id="txtValidateCode"]').send_keys(vcode)
            self.driver.find_element_by_xpath('//*[@id="btnLogin"]').click()
            time.sleep(2)
            # TODO 已完
            validate_handles = self.driver.window_handles
            # print validate_handles
            for v in validate_handles:
                self.driver.switch_to_window(v)

            self.search_company()

    def select_page_number(self):
        '''
        选择每页显示的条数
        :return:
        '''
        self.driver.implicitly_wait(10)

        chains = ActionChains(self.driver)
        button = self.driver.find_element_by_xpath('//*[@id="14_button"]')
        #将页面滚动条拖到底部
        button.send_keys(Keys.DOWN)
        time.sleep(random.randint(1, 3))
        button.send_keys(Keys.DOWN)
        time.sleep(random.randint(1, 3))
        button.send_keys(Keys.DOWN)
        time.sleep(random.randint(1, 3))
        button.send_keys(Keys.DOWN)
        time.sleep(random.randint(1, 3))
        button.send_keys(Keys.DOWN)
        time.sleep(random.randint(1, 3))
        button.send_keys(Keys.DOWN)
        # ccc = chains.context_click(button)
        #
        ccc = chains.click(button)
        time.sleep(random.randint(1, 3))
        ccc.send_keys(Keys.ARROW_DOWN)
        time.sleep(random.randint(1, 3))
        ccc.send_keys(Keys.ARROW_DOWN)
        time.sleep(random.randint(1, 3))
        ccc.send_keys(Keys.ARROW_DOWN)
        time.sleep(random.randint(1, 3))
        ccc.send_keys(Keys.ARROW_DOWN)
        time.sleep(2)
        ccc.click(self.driver.find_element_by_xpath('//*[@id="14_input_20"]'))
        chains.perform()
        time.sleep(5)

    def search_company(self):
        '''
        查询公司
        :return:
        '''
        try:
            # 隐式等待，如果被定为的元素30秒内没有出现，则出现NoSuchElementException异常
            self.driver.implicitly_wait(30)
            gover_search_keys = self.driver.find_elements_by_xpath('//*[@id="gover_search_key"]')
            if gover_search_keys:
                for gsk in gover_search_keys:
                    gsk.clear()
                    gsk.send_keys(company_name)
            # TODO 在查询第二个企业的时候必须触发此操作(前提企业名称是从数据库里查询的)
            # self.driver.find_element_by_xpath('//*[@id="conditionCollect"]/ul/li[3]/a').click()
            # TODO 读取企业库，获取所有的企业名称，待完成

            searchBoxs = self.driver.find_elements_by_xpath('//*[@id="searchBox"]/div/div[3]/button')
            if searchBoxs:
                for sb in searchBoxs:
                    sb.click()
            # 窗口设置成最大化
            self.driver.maximize_window()

            time.sleep(5)
            handles = self.driver.window_handles
            # print 'handles = %s'%handles
            for h in handles:
                self.driver.switch_to_window(h)
        except Exception,e:
            logger.error(e)


if __name__ == '__main__':
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', 'court'])
