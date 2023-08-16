---
title: "Python--百度站长平台主动推送"
categories: [ "Python","工具分享" ]
tags: [ "Python","建站经验" ]
draft: false
slug: "348"
date: "2019-07-25 17:45:00"
---

# 起因

这是一篇网站折腾介绍

`soapffz`已经写了`40+`文章了：

![][1]

经常和别人介绍自己的网站，别人总是会问“访问量有多少？”

`soapffz`只能回答：“由于没向百度推送，所以百度搜不到”

于是，这篇文章将捋一捋为什么没向百度推送以及解决方案

分为两个部分，`sitemap`生成和向百度推送

# sitemap 生成

## 前期挖的坑

刚建设完网站时，在每篇文章写完之后链接中会存在一个`index.php`

为了把这个`index.php`去掉，变成这些链接：

```
https://soapffz.com/sec/247.html
https://soapffz.com/python/245.html
https://soapffz.com/tools/239.html
https://soapffz.com/sec/233.html
```

我在后台做了如下操作：

![][2]

这也导致我使用一些`sitemap`自动生成插件的时候，会变成这样：

![][3]

## 折腾

这其中除了`sitemap`生成插件我也使用过在线网站，比如[这个][4]

![][5]

可以看到花了八分半，爬了 124 条链接，点击`View Sitemap Details`查看详情

点击`Other Downloads`处所示按钮下载所有格式的文件:

![][6]

可以看到爬取的链接都是正常的，但是问题也来了，

这样生成`sitemap`也太费劲了吧，后面也尝试过使用`Python`去爬取网站所有 url

但是想想实在没必要，就一个`url`格式问题而已

## 最终解决方案

于是最终决定放弃在`url`中包含目录字段：

![][7]

然后使用前面介绍的八云酱的[插件][8]即可生成`sitemap`：

![][9]

然后尝试向百度提交：

![][10]

可以看到链接提交成功了

# 向百度主动推送

`sitemap`处理完了还不够，我们可以使用主动推送和`sitemap`结合起来使得百度收录更快

百度的主动推送方式：

![][11]

大概就是意思就是把`url.txt`带上自己的`token`传输给百度资源平台

我用`Python`参考网上的文章写了一个脚本

逻辑就是解析网站当前的`sitemap.xml`然后获取`urls`带上自己的`token`和网站名称

使用`request`库的`post`方式提交一下然后查看返回状态即可

全代码如下：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 从网站的sitemap.xml抓取url并向百度站长平台主动推送
@time: 2019-07-25
'''

import requests
import xmltodict


class BaiduLinkSubmit(object):
    def __init__(self, site_domain, sitemap_url, baidu_token):
        self.site_domain = site_domain
        self.sitemap_url = sitemap_url
        self.baidu_token = baidu_token
        self.urls_l = []  # 存储需要爬取的url
        self.parse_sitemap()

    def parse_sitemap(self):
        # 解析网站的sitemap.xml获取所有urls
        try:
            data = xmltodict.parse(requests.get(self.sitemap_url).text)
            self.urls_l = [t["loc"] for t in data["urlset"]["url"]]
        except Exception as e:
            print("爬取sitemap.xml报错:", e)
            return
        self.push()

    def push(self):
        url = "http://data.zz.baidu.com/urls?site={}&token={}".format(
            self.site_domain, self.baidu_token)
        headers = {"Content-Type": "text/plain"}
        r = requests.post(url, headers=headers, data="\n".join(self.urls_l))
        data = r.json()
        print("成功推送{}条url到百度搜索资源平台".format(data.get("success", 0)))
        print("今天还剩余的可推送条数:", data.get('remain', 0))
        not_same_site = data.get('not_same_site', [])
        not_valid = data.get("no_valid", [])
        if len(not_same_site) > 0:
            print("由于不是本站url而未处理的url有{}条：".format(len(not_same_site)))
            for t in not_same_site:
                print(t)
        if len(not_valid) > 0:
            print("不合法的url有{}条：".format(len(not_valid)))
            for t in not_valid:
                print(t)


if __name__ == "__main__":
    site_domain = "https://soapffz.com"  # 在这里填写你的网站
    sitemap_url = "https://soapffz.com/sitemap.xml"  # 在这里填写你的sitemap.xml完整链接
    baidu_token = ""  # 填写你的百度token
    BaiduLinkSubmit(site_domain, sitemap_url, baidu_token)
```

我这里测试了三次，分别对应正常情况、我关掉`sitemap`插件和我乱写`sitemap`的情况

效果如下：

![][12]

# MIP&AMP 网页加速

百度站长平台是这么介绍的：

> 1. MIP(Mobile Instant Page - 移动网页加速器)，是一套应用于移动网页的开放性技术标准。通过提供 MIP-HTML 规范、MIP-JS 运行环境以及 MIP-Cache 页面缓存系统，实现移动网页加速。
> 2. AMP（Accelerated Mobile Pages）是谷歌的一项开放源代码计划，可在移动设备上快速加载的轻便型网页，旨在使网页在移动设备上快速加载并且看起来非常美观。百度目前可支持 AMP 提交。

反正就是针对移动端的加速，肯定对`SEO`有好处

这里使用的插件是[Holmesian][13]大佬的工具[Typecho-AMP][14]

插件后台界面如图所示：

![][15]

可以看到还支持百家号，但是我这里不需要@(滑稽)，所以只要设置接口就可以了，

然后在控制台的下拉菜单中可以看到有个推送`AMP/MIP`到百度按钮：

![][16]

点进去如图所示：

![][17]

尝试推送一下：

![][18]

发现推送不了，折腾了一会主机也没弄好，看了下主动推送规则发现非常有趣

和基础链接提交就在链接后面加了一个`mip/amp`，返回的参数变为`success_mip/success_amp`等

所以把上面的代码改一下，就把推送`url`和推送给`mip/amp`的代码放在一起同时推送：

[1]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_174611.png
[2]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_165655.png
[3]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_165630.png
[4]: https://www.xml-sitemaps.com/
[5]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_175048.png
[6]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_175342.png
[7]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_194055.png
[8]: https://github.com/bayunjiang/typecho-sitemap
[9]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_195434.png
[10]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_195516.png
[11]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_195740.png
[12]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_204410.png
[13]: https://holmesian.org/
[14]: https://github.com/holmesian/Typecho-AMP
[15]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190727_001042.png
[16]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190727_001256.png
[17]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_165237.png
[18]: https://img.soapffz.com/archives_img/2019/07/25/archives_20190725_165247.png