# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# https://www.pixiv.net/artworks/83362234
import time
import scrapy
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class PixivcrawlerVer2SpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class PixivcrawlerVer2DownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["pageLoadStrategy"] = "none"

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-cgu')
        chrome_options.add_argument('window-size=1920x1500')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        path = r'C:\Users\83464\Documents\webdrivers\chromedriver.exe'
        self.pre_driver = webdriver.Chrome(executable_path=path, options=chrome_options)


    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if request.url == "https://accounts.pixiv.net/login":
            response = self.get_cookies(request, spider)
            response.pri_url = request.url
            response.rf = False
            return response
        else:
            print("Getting page source")
            self.pre_driver.get(request.url)
            time.sleep(5)
            try:
                WebDriverWait(self.pre_driver, 15).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[@role="presentation"]//a')))
            #     //div[@role="presentation"]//a/@href
            except:
                pass
            js = 'document.documentElement.scrollTop=10000'
            self.pre_driver.execute_script(js)
            time.sleep(1)
            self.pre_driver.execute_script(js)
            time.sleep(1)

            response = scrapy.http.HtmlResponse(url=self.pre_driver.current_url,
                                                body=self.pre_driver.page_source,
                                                request=request,
                                                encoding='utf-8')
            response.pri_url = request.url
            try:
                err = response.xpath('//div[@id="main-message"]/h1/span//text()').getall()[0]
                count = 0
                while err == "无法访问此网站" and count < 5:
                    # refresh
                    self.pre_driver.execute_script('window.open("https://www.google.com/search?q=b")')
                    handles = self.pre_driver.window_handles[0]
                    self.pre_driver.switch_to.window(self.pre_driver.window_handles[1])
                    try:
                        WebDriverWait(self.pre_driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//input')))
                    except:
                        pass
                    self.pre_driver.close()
                    self.pre_driver.switch_to.window(handles)
                    self.pre_driver.get(request.url)
                    try:
                        WebDriverWait(self.pre_driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//div[@role="presentation"]//a')))
                    except:
                        pass
                    js = 'document.documentElement.scrollTop=10000'
                    self.pre_driver.execute_script(js)
                    time.sleep(1)
                    self.pre_driver.execute_script(js)
                    time.sleep(1)
                    response = scrapy.http.HtmlResponse(url=self.pre_driver.current_url,
                                                        body=self.pre_driver.page_source,
                                                        request=request,
                                                        encoding='utf-8')
                    response.pri_url = request.url
                    spider.cookies = self.pre_driver.get_cookies()
                    count = count + 1
                    err = response.xpath('//div[@id="main-message"]/h1/span//text()').getall()[0]
                if count == 5:
                    response.rf = True
                else:
                    response.rf = False

                return response
            except:
                response.rf = True
                return response

    def process_response(self, request, response, spider):
        response.rf = False
        return response


    def get_cookies(self, re, spider):
        self.pre_driver.get(re.url)
        # login
        while True:
            con = input("login complited?(Y/n)")
            if con == 'y' or con == 'Y':
                response = scrapy.http.HtmlResponse(url=self.pre_driver.current_url,
                                                    body=self.pre_driver.page_source,
                                                    request=re,
                                                    encoding='utf-8')
                spider.pre_cookies = self.pre_driver.get_cookies()
                return response


    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
