---
title: "Python3 - 用纯真ip数据库批量查询ip归属地"
categories: [ "Python","工具分享" ]
tags: [ "Python","渗透","信息收集","ip归属" ]
draft: false
slug: "245"
date: "2019-06-28 16:38:00"
---

# 起因

正在摸鱼写网站日志分析文章的时候发现需要批量使用纯真 ip 数据库来查询 ip 地址归属地\

于是二层摸鱼先写这篇`Python`批量查询 ip 归属地的文章，可谓是摸鱼中的摸鱼，杠上开花

这篇文章同时归类于`Python`和`工具分享`

# 纯真 IP 地址数据库介绍

> 纯真 IP 数据库解析 qqwry.dat 库文件。 QQWry IP 数据库 纯真版收集了包括中国电信、中国移动、中国联通、长城宽带、聚友宽带等 ISP 的最新准确 IP 地址数据。IP 数据库每 5 天更新一次，需要定期更新最新的 IP 数据库。

软件长这个样子：

![][1]

由于其经常更新，我找到了一个[`GitHub`项目][2]，每天自己扫描并同步最新的`qqwry.dat`

要获取最新的`qqwry.dat`[点我即可下载][3] (挂梯子)

你也可以下载这个最新版重命名覆盖掉原版的就不用一直下载纯真数据库安装包了

# Python 批量查询

全面的库请参考文末第一篇参考文章`qqwry-python3`

这个作者写的工具，已经上传到了`pypi`，直接`pip install qqwry-py3`就可使用

~~ 当然我这个只是简单实现批量读取`ip`归属地，后面如果有其他想法会在这篇文章更新 ~~

~~ 最终版代码如下：~~

** 发现好像很难写的亚子，就先用成熟的 qqwry 库吧，后面有兴趣再写(估计不会再写了) **

::quyin:1huaji::

批量从文本查询 ip 地址并输出结果代码如下：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 使用纯真ip数据库qqwry.dat批量查询txt内ip的归属地
@time: 2019-06-28
'''

from qqwry import QQwry
from IPy import IP


def batch_query_and_print():
    q = QQwry()
    q.load_file('qqwry.dat')
    with open('ip.txt') as f:
        ip_list = f.read().splitlines()
        for read_content in ip_list:
            try:
                IP(read_content)
            except:
                print("有不符合规范的IP地址，请检查后重新运行")
                exit(0)
    address_list = [q.lookup(ip) for ip in ip_list]
    for i, j in zip(ip_list, address_list):
        query_results = i+" "+j[0]+" "+j[1]
        print(query_results)
        with open("query_results.txt", 'a', encoding='utf-8') as f:
            f.writelines(query_results+"\n")


if __name__ == "__main__":
    batch_query_and_print()
```

`pip install`分别安装`qqwry`和`IPy`库

将要查询的`ip`放到`ip.txt`并和`qqwry.dat`、`.py`文件在同一个目录即可运行

效果如下：

![][4]

参考文章：

- [qqwry-python3][5]

[1]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190628_170740.png
[2]: https://github.com/out0fmemory/qqwry.dat
[3]: https://raw.githubusercontent.com/out0fmemory/qqwry.dat/master/qqwry_lastest.dat
[4]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190628_193933.png
[5]: https://github.com/animalize/qqwry-python3