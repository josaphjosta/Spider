import os
import time
import re
import requests
import pandas
from pandas import Series, DataFrame


dir_path = 'pixiv_img'


class PixivcrawlerVer2Pipeline(object):
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'
        }
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        self.file_list = DataFrame({'0': []})
        self.img_list = DataFrame({'0': []})  # img & url


    def open_spider(self, spider):
        print("Pipeline ON")

        # pipeline 去重
        if os.path.exists(dir_path):
            self.img_list = os.listdir(dir_path)
            self.img_list = DataFrame(data={'img': self.img_list})
            print('Img list loaded')
            print(self.img_list.head())
        # file_list.append(DataFrame({'0': url_list}))
        if os.path.exists('./img_list.csv'):
            self.file_list = pandas.read_csv('./img_list.csv')
            spider.src_list = self.file_list['url'].dropna()
            print('csv file loaded')
            print(self.file_list.head())

        if len(self.file_list) or len(self.img_list):
            self.img_list = self.img_list.append(self.file_list, ignore_index=True, sort=True).drop_duplicates()

    def close_spider(self, spider):
        print('closing...' + str(spider.src_list))
        file = DataFrame({'img': self.img_list['img'].dropna()}).append(DataFrame({'url': spider.src_list}), ignore_index=True, sort=True)
        file.drop_duplicates(inplace=True)
        file.to_csv(path_or_buf='./img_list.csv', index=False)
        print('history img list saved')
        print("Pipeline OFF")

    def process_item(self, item, spider):
        # try:
        print("----------PIPELINE----------")
        print("Start download")
        srcs = item['srcs']
        self.headers['Referer'] = item['referer']
        index = item['index']
        for src_t in srcs:
            # try:
            src_m = re.findall(r'(.*_p)0(\..*$)', src_t)[0]
            for i in range(index):
                src = src_m[0] + str(i) + src_m[1]
                fn = os.path.basename(src)
                filepath = os.path.join(dir_path, fn)
                session = requests.session()
                for cookie in spider.pre_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                session.headers.clear()
                if not os.path.exists(filepath):
                    print(src)
                    if not self.img_list.empty:
                        if self.img_list['img'].str.count(fn).sum():
                            print('Img have been downloaded before')
                            continue
                    for i_t in range(3):
                        try:
                            r = session.get(src, headers=self.headers)
                        except:
                            print("Download Error")

                    with open(filepath, 'wb') as fp:
                        fp.write(r.content)
                    print("Download complited")
                    self.img_list = self.img_list.append(DataFrame({'img': [fn]}), ignore_index=True, sort=True)
                    time.sleep(1)
                else:
                    print("Img existed or downloading failed")
            return item
            # except:
            #     continue
        # except:
        #     print("Void src")
