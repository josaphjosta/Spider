# 实验版本，不会更新，估计有点bug，这辈子第一次加这么多注释
# 修改 #16 行url，爬取目标近30天的视频信息，可改天数，见 #30 行
# 有 Index(['name', 'date', '视频观看量', '粉丝观看率', '视频预估价值', '点赞百分比', '评论数', '粉丝互动率',
#        ' 粉丝数', ' 总视频数', ' 总观看量'],
#       dtype='object')

import requests
import lxml
from lxml import html

import numpy as np
from pandas import Series, DataFrame

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
}

url = "https://cn.noxinfluencer.com/youtube/channel/UCS9uQI-jC3DE0L4IpXyvr6w"
# 自己粘贴覆盖掉，这里是tskk的主页


def get_day_url(mp_url):
    # 从页面构造ajax链接，获取详情页面的url

    r = requests.get(url=mp_url, headers=header)
    tree = html.etree.HTML(r.text)
    cpmMin = tree.xpath('//input[@id="cpmMin"]/@value') # 获取两个意义不明的参数，以构造Ajax链接
    cpmMax = tree.xpath('//input[@id="cpmMax"]/@value')
    ajax_url = "https://cn.noxinfluencer.com/api/youtube/detail/dimension/?window={}&channelId=UCS9uQI-jC3DE0L4IpXyvr6w" \
            "&startDate={}&cpmMin={}&cpmMax={} ".format('29', '2020-09-27', cpmMin, cpmMax)
    # 前面两个可以改，对应日期和到现在有多少天，可以一次性获得数量大于30的url

    d_url = 'https://cn.noxinfluencer.com'

    r = requests.get(url=ajax_url, headers=header).json()   # 开始请求ajax, 以构造详情界面的url
    tree = html.etree.HTML(r['retData']['dom'])
    detail_urls = [d_url + i for i in tree.xpath('//div[@class="table-container"]//@href')]

    return detail_urls


def get_day_info(detail_url):
    # 抓取每一天的信息（视频的）
    r = requests.get(url=detail_url, headers=header)
    print(r.raise_for_status())
    tree = html.etree.HTML(r.text)
    r_data = tree.xpath('//div[@class="detail-content"]//li')
    data = {}
    basic_info = tree.xpath('//div[@class="info-block"]//span//text()')
    data['name'] = [basic_info[0]]
    data['date'] = [basic_info[-1]]
    for detail in r_data:
        data[detail.xpath('.//div[@class="title"]//text()')[0]] = detail.xpath('.//div[@class="content"]/text()')

    for i in range(len(basic_info))[1::2]: # 取日期之类的基本信息
        if i == len(basic_info) - 1:
            break
        data[basic_info[i + 1]] = [basic_info[i]]

    print(data)

    data_list = DataFrame(data=data)

    return data_list


# 主函数
detail_urls = get_day_url(url) # url在最上面改
indv_data = []
for de_url in detail_urls:
    indv_data.append(get_day_info(de_url))

data_list = indv_data[0]
for data in indv_data[1:]: #做成DataFrame的表格
    data_list = data_list.append(data, ignore_index=True)

# 保存z当前文件夹
data_list.to_csv(path_or_buf='./data_list.csv', index=False)