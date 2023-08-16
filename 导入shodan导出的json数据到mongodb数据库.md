---
title: "导入shodan导出的json数据到mongodb数据库"
categories: ["安全技术"]
tags: ["数据库", "Navicat", "shodan"]
draft: false
slug: "415"
date: "2019-12-28 21:09:00"
---

## 事情起因

年底冒泡，闲来瞎搞

上次有幸 1 美元搞到[shodan][1]的终身会员，一个月可以下载 20 次数据，每次 10000 条上限

无聊存一下 shodan 上能搜索到的 phpmyadmin 的数据

**申明：本文所用到的数据均来自合法来源并且仅供测试使用，本人已于 24 小时内删除**

## shodan 下载数据

shodan 是比较老牌的网络空间安全引擎，主要功能是搜索网上公开的各种数据库和网站

可配合 msf 使用，但是个人觉得网页上左边的分类快捷跳转比较方便

![][2]

可以看到中国在网络上能搜索到的 phpmyadmin 服务器大概有 11000 多台，刚好 shodan1 积分能下载 10000 条数据

我就下载了 10000 条数据

下载时选择格式，XML 已经不建议被使用，于是我下载了 json

打开下载完的数据看一眼，发现是按行排列的

![][3]

尝试着用 navicat 的导入功能直接导入格式化过的 json 数据失败了，于是直接莽 mongodb 数据库

## mongodb 数据库导入

也尝试过了用 navicat 导入 mongodb 数据库，也是一样的显示 json 数据没有标准化

mongodb 的安装在以前的文章介绍过了：[《Win10 安装 mongodb》][4]

安装后我们进入 mongodb 默认的路径：

    C:\Program Files\MongoDB\Server\4.2\bin

在此处打开 cmd，输入：

    mongo.exe

打开 mongodb 命令行交互，创建一个数据库：

    use shodan

exit 退出使用 mongoimport.exe 导入 json 数据：

    mongoimport.exe --db shodan_data --collection phpmyadmin_data --file E:\share\shodan-export.json\shodan_data.json

`db`是我们创建的数据库(其实不创建直接指定也可以)，`collection`是集合名称，类似`mysql`中的表

`file`指定的是我们下载下来的`shodan`的`json`文件：

![][5]

导入 2，3 秒就好了，用`navicat`打开看一眼：

![][6]

嗯，数据已经导入完毕了，可以开始批量。。???我在说什么？

**PS:navicat 作为显示数据库的工具还是非常优秀的，但是导入数据这方面做的真心差**

本文完。

[1]: https://www.shodan.io/
[2]: https://img.soapffz.com/archives_img/2019/12/28/archives_20191228_211626.png
[3]: https://img.soapffz.com/archives_img/2019/12/28/archives_20191228_212153.png
[4]: https://soapffz.com/92.html
[5]: https://img.soapffz.com/archives_img/2019/12/28/archives_20191228_222624.png
[6]: https://img.soapffz.com/archives_img/2019/12/28/archives_20191228_223527.png
