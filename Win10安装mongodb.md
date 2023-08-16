---
title: "Win10安装mongodb"
categories: [ "工具分享" ]
tags: [ "mongodb","数据库" ]
draft: false
slug: "92"
date: "2019-04-21 13:34:00"
---

# 事情起因

前段时间写本地射弓库搭建的时候，因为我是每个裤子创建一个表，后面可以多表联合查询，用主键外键之类的

所以用的是经典的**关系型数据库**：`mysql`

当然`mysql`在数据超亿的时候性能可能会大幅下降，这个坑我们后面再填

今天来挖一个新坑：**非关系型数据库**典型例子：`MongoDB`

关系型数据库与非关系型数据库的区别比较，参考：[关系数据库与非关系数据库][1]

> 面向高性能并发读写的 key-value 数据库：

> key-value 数据库的主要特点即使具有极高的并发读写性能，Redis,Tokyo Cabinet,Flare 就是这类的代表

> 面向海量数据访问的面向文档数据库：

> 这类数据库的特点是，可以在海量的数据中快速的查询数据，典型代表为 MongoDB 以及 CouchDB

# 下载

https://www.mongodb.com/download-center/community

下载`community`社区版就够我们用了：

![][2]

# 安装

我选择了`complete`完整版安装，在服务配置界面，建议选择配置为服务(以前的安装好像都是要手动到安装目录配置为服务，现在可以直接傻瓜配置)

然后默认选择配置为网络服务即可，配置为网络的话网络和本地都能用：

![][3]

然后取消勾选下载图形化界面：

![][4]

安装完在服务中就能看到`MongoDB Server`服务了，开机自启的：

![][5]

其他的用法也不说了，因为我使用`Navicat`家的`Navicat for mongodb`来可视化管理这个数据库

参考文章：[MongoDB 教程 | 菜鸟教程][6]

本文完

[1]: https://www.cnblogs.com/suncan0/p/4735129.html
[2]: https://img.soapffz.com/archives_img/2019/04/21/archives_20190421_133044.png
[3]: https://img.soapffz.com/archives_img/2019/04/21/archives_20190421_133212.png
[4]: https://img.soapffz.com/archives_img/2019/04/21/archives_20190421_133234.png
[5]: https://img.soapffz.com/archives_img/2019/04/21/archives_20190421_133340.png
[6]: http://www.runoob.com/mongodb/mongodb-tutorial.html