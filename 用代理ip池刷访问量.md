---
title: "用代理ip池刷访问量"
categories: ["Python"]
tags: ["Python", "代理"]
draft: false
slug: "17"
date: "2019-01-23 13:23:00"
---

# 前言

不管是暴力破解还是反爬虫，代理池都是必不可少的一个条件

关于代理池的获取，我们在上一篇文章：《多线程爬取西刺高匿代理并验证可用性》已经介绍过了

我们就用这篇文章获得的验证过的代理来试一下刷访问量

# 丑陋的代码实现

大部分代码实现都是照搬上面说的这篇文章的

唯一不同的是学到一个库叫做 fake_useragent，可以用它生成随机的 User-Agent，简单示例代码如下：

```
from fake_useragent import UserAgent
ua = UserAgent()  # 用于生成User-Agent
headers = {"User-Agent": ua.random} # 获得一个随机的User-Agent
print(headers)
```

需要指定浏览器的 User-Agent 可以参考这篇文章：https://blog.csdn.net/qq_29186489/article/details/78496747

全代码：

```
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 用代理ip池刷访问量
@time: 2019-01-23
'''
import os
import requests
from fake_useragent import UserAgent
from multiprocessing import Pool
import timeit


url = "https://soapffz.com/"  # 要刷取的网页
ua = UserAgent()  # 用于生成User-Agent
path = os.path.join(os.path.expanduser("~")+"\\")
http_proxy_path = os.path.join(
    path+"Desktop"+"\\"+"http_proxy.txt")  # 这是我自己的代理ip的位置
https_proxy_path = os.path.join(
    path+"Desktop"+"\\"+"https_proxy.txt")  # 根据自己位置不同自己修改
http_proxy = []  # 存储http代理
https_proxy = []  # 存储https代理


def brush_visits(proxies):
    proxy_type = proxies.split(":")[0]
    if proxy_type == 'http':
        proxy = {'http': proxies}
    else:
        proxy = {'https': proxies}
    headers = {"User-Agent": ua.random}  # 获得一个随机的User-Agent
    req = requests.get(url, headers=headers, proxies=proxy, timeout=10)
    if req.status_code == 200:
        print("此代理访问成功：{}".format(proxies))


if __name__ == "__main__":
    start_time = timeit.default_timer()
    if not os.path.exists(http_proxy_path):
        print("代理都没准备好还想刷访问量？滚吧您！")
        os._exit(0)
    with open(http_proxy_path, 'r') as f:
        http_proxy = f.read().splitlines()
    with open(https_proxy_path, 'r') as f:
        https_proxy = f.read().splitlines()
    pool1 = Pool()
    pool2 = Pool()
    for proxies in http_proxy:
        pool1.apply_async(brush_visits, args=(proxies,))
    for proxies in https_proxy:
        pool2.apply_async(brush_visits, args=(proxies,))
    pool1.close()
    pool2.close()
    pool1.join()
    pool2.join()
    end_time = timeit.default_timer()
    print("代理池已经用完了，共用时耗时{}s".format(end_time-start_time))
```

效果展示如下：

![][1]

---

# 更新

[2019-08-27 更新]前面写的是基于文件的读取，现在看来有点沙雕，加上最近有用到这个的需求，更新下

前期准备只需要你安装好`Mongodb`数据库即可，可参考我之前写过的文章《Win10 安装 mongodb》

然后就可以直接运行此代码，修改其中想要刷取的界面即可，全代码如下：

```
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 用代理ip池批量刷取网站访问量(读取本地mongodb数据库中的代理集合)
@time: 2019-08-27
'''

from os import popen
from threading import Thread  # 多线程
from pymongo import MongoClient
from requests import get
from lxml import etree  # 解析站点
from re import split  # re解析库
from telnetlib import Telnet  # telnet连接测试代理有效性
from fake_useragent import UserAgent
from multiprocessing import Pool


def brush_visits(url, proxy):
    # 用单个代理访问单个页面
    try:
        ua = UserAgent()  # 用于生成User-Agent
        headers = {"User-Agent": ua.random}  # 获得一个随机的User-Agent
        req = get(url, headers=headers, proxies=proxy, timeout=0.3)
        if req.status_code == 200:
            print("此代理{}贡献了一次访问".format(proxy))
    except Exception as e:
        pass


class batch_brush_visits(object):
    def __init__(self, url):
        self.url = url
        self.ua = UserAgent()  # 用于生成User-Agent
        self.run_time = 0  # 运行次数
        self.conn_db()
        self.get_proxies_l()

    def conn_db(self):
        # 连接数据库
        try:
            # 连接mongodb，得到连接对象
            self.client = MongoClient('mongodb://localhost:27017/').proxies
            self.db = self.client.xici  # 指定proxies数据库，这个类都使用这个数据库，没有数据不会自动创建
            self.refresh_proxies()
        except Exception as e:
            print("数据库连接出错")
            exit(0)

    def refresh_proxies(self):
        if "xici" in self.client.list_collection_names():
            # 每次初始化时删除已有的集合
            self.db.drop()
            t = Thread(target=self.xici_nn_proxy_start)
            t.start()
            t.join()

    def get_proxies_l(self):
        # 读取对应集合中ip和port信息
        collection_dict_l = self.db.find(
            {}, {"_id": 0, "ip": 1, "port": 1, "type": 1})
        self.proxies_l = []
        for item in collection_dict_l:
            if item["type"] == 'http':
                self.proxies_l.append(
                    {"http": "{}:{}".format(item['ip'], item['port'])})
            else:
                self.proxies_l.append(
                    {"https": "{}:{}".format(item['ip'], item['port'])})
        if len(self.proxies_l) == 0:
            print("没有获取到代理，刷个屁...")
            exit(0)
        else:
            self.brush_visits_start()

    def xici_nn_proxy_start(self):
        xici_t_cw_l = []  # 爬取线程列表
        self.xici_crawled_proxies_l = []  # 每次爬取之前先清空
        for i in range(1, 11):  # 爬取10页代理
            t = Thread(target=self.xici_nn_proxy, args=(i,))
            xici_t_cw_l.append(t)  # 添加线程到线程列表
            t.start()
        for t in xici_t_cw_l:  # 等待所有线程完成退出主线程
            t.join()
        # 插入数据库
        self.db_insert(self.xici_crawled_proxies_l)

    def xici_nn_proxy(self, page):
        # 西刺代理爬取函数
        url = "https://www.xicidaili.com/nn/{}".format(page)
        # 这里不加user-agent会返回状态码503
        req = get(url, headers={"User-Agent": self.ua.random})
        if req.status_code == 200:
            # 状态码是其他的值表示ip被封
            content = req.content.decode("utf-8")
            tree = etree.HTML(content)
            # 用xpath获得总的ip_list
            tr_nodes = tree.xpath('.//table[@id="ip_list"]/tr')[1:]
            for tr_node in tr_nodes:
                td_nodes = tr_node.xpath('./td')  # 用xpath获得单个ip的标签
                speed = int(split(r":|%", td_nodes[6].xpath(
                    './div/div/@style')[0])[1])  # 获得速度的值
                conn_time = int(split(r":|%", td_nodes[7].xpath(
                    './div/div/@style')[0])[1])  # 获得连接时间的值
                if(speed <= 85 | conn_time <= 85):  # 如果速度和连接时间都不理想，就跳过这个代理
                    continue
                ip = td_nodes[1].text
                port = td_nodes[2].text
                ip_type = td_nodes[5].text.lower()
                self.get_usable_proxy(ip, port, ip_type, "xici")

    def get_usable_proxy(self, ip, port, ip_type, proxy_name):
        proxies_l = {"ip": ip, "port": port, "type": ip_type}
        if proxies_l not in self.xici_crawled_proxies_l:
            try:
                # 用telnet连接一下，能连通说明代理可用
                Telnet(ip, port, timeout=0.3)
            except:
                pass
            else:
                self.xici_crawled_proxies_l.append(proxies_l)

    def db_insert(self, proxies_list):
        if proxies_list:
            # 传入的列表为空则退出
            self.db.insert_many(proxies_list)  # 插入元素为字典的列表
            print(
                "数据已插入完毕!\n此次共插入{}个代理到xici集合中!".format(len(proxies_list)))
        else:
            print(
                "爬到的代理列表为空！\n如果你很快看到这条消息\n估计ip已被封\n请挂vpn!\n否则最新代理都已在数据库中了\n不用再爬了!")

    def brush_visits_start(self):
        # 用获得的代理刷取页面
        try:
            self.run_time += 1
            pool = Pool()
            for proxy in self.proxies_l:
                pool.apply_async(brush_visits(self.url, proxy))
            pool.close()
            pool.join()
            if self.run_time == 100:
                print("已刷取一百次，重新获取代理")
                self.refresh_proxies()
            print("已刷取完一遍")
            self.brush_visits_start()
        except Exception as e:
            print("程序运行报错退出:{}".format(e))
            exit(0)


if __name__ == "__main__":
    url = "https://soapffz.com/3.html"  # 在这里填写需要刷取的url
    batch_brush_visits(url)
```

效果如下：

![][2]

另外，文中的代码设计的是为一个`url`刷取，如果你需要同时刷取多个`url`

需要使用到笛卡尔乘积，使用例子如下：

```
from itertools import product

urls_l = ["https://soapffz.com/279.html",
          "https://soapffz.com/timeline.html", "https://soapffz.com/372.html"]
proxies_l = ["120.120.120.121", "1.1.1.1", "231.220.15.2"]
paramlist = list(product(urls_l, proxies_l))
for i in range(len(paramlist)):
    print(paramlist[i])
```

效果如下：

![][3]

所以，你需要如下改动：

- 导入这个库：

```
from itertools import product
```

- `main`函数中的 url 改为列表

```
if __name__ == "__main__":
    urls_l = ["https://soapffz.com/3.html"]  # 在这里填写需要刷取的urls列表
    batch_brush_visits(urls_l)
```

- 刷取目标改为笛卡尔积

`batch_brush_visits`类中的`brush_visits_start`部分代码改动如下：

```
            pool = Pool()
            for proxy in self.proxies_l:
                pool.apply_async(brush_visits(self.url, proxy))
            pool.close()
            pool.join()
```

改为

```
            paramlist = list(product(self.urls_l, self.proxies_l))
            pool = Pool()
            for i in range(len(paramlist)):
                pool.apply_async(brush_visits(paramlist[i]))
            pool.close()
            pool.join()
```

- 改动访问函数

`brush_visits`函数改动如下，由

```
def brush_visits(url, proxy):
    # 用单个代理访问单个页面
    try:
        ua = UserAgent()  # 用于生成User-Agent
        headers = {"User-Agent": ua.random}  # 获得一个随机的User-Agent
        req = get(url, headers=headers, proxies=proxy, timeout=0.3)
        if req.status_code == 200:
            print("此代理{}贡献了一次访问".format(proxy))
    except Exception as e:
        pass
```

改为：

```
def brush_visits(paramlist):
    # 用单个代理访问单个页面
    try:
        url = paramlist[0]
        proxy = paramlist[1]
        ua = UserAgent()  # 用于生成User-Agent
        headers = {"User-Agent": ua.random}  # 获得一个随机的User-Agent
        req = get(url, headers=headers, proxies=proxy, timeout=0.3)
        if req.status_code == 200:
            print("此代理:{}贡献一次访问".format(proxy))
    except Exception as e:
        pass
```

就差不多了，可以实现每个`代理`访问一次每一个`url`的效果

本文完。

[1]: https://img.soapffz.com/archives_img/2019/01/23/archives_20190123_135526.png
[2]: https://img.soapffz.com/archives_img/2019/01/23/archives_20190827_143550.png
[3]: https://img.soapffz.com/archives_img/2019/01/23/archives_20190827_145442.png
