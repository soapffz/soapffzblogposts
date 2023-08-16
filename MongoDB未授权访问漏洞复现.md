---
title: "MongoDB未授权访问漏洞复现"
categories: [ "安全技术","工具分享" ]
tags: [ "代理","漏洞利用","MSF","mongodb" ]
draft: false
slug: "457"
date: "2020-01-29 22:30:00"
---

## 事情起因

持续整理笔记中

参考文章：

- [MongoDB 未授权访问漏洞复现][1]
- [常见未授权访问漏洞总结][2]

本来准备参考其他文章用`docker`自己搭建一个测试了，结果竟然让我搜到了`shodan`关键词

## 0x00 简介

> MongoDB 是一个基于分布式文件存储的数据库。由 C++ 语言编写。旨在为 WEB 应用提供可扩展的高性能数据存储解决方案。
> MongoDB 是一个介于关系数据库和非关系数据库之间的产品，是非关系数据库当中功能最丰富，最像关系数据库的。

## 0x01 漏洞危害

> 开启 MongoDB 服务时不添加任何参数时,默认是没有权限验证的,登录的用户可以通过默认端口无需密码对数据库任意操作（增删改高危动作）而且可以远程访问数据库。

## 0x02 漏洞成因

> 在刚安装完毕的时候 MongoDB 都默认有一个 admin 数据库,此时 admin 数据库是空的,没有记录权限相关的信息！当 admin.system.users 一个用户都没有时，即使 mongod 启动时添加了—auth 参数,如果没有在 admin 数据库中添加用户,此时不进行任何认证还是可以做任何操作(不管是否是以—auth 参数启动),直到在 admin.system.users 中添加了一个用户。加固的核心是只有在 admin.system.users 中添加用户之后，mongodb 的认证,授权服务才能生效

## 0x03 漏洞复现

### shodan 搜索对应数据

搜素某关键词得到未授权的`MongoDB`数据库：

![][3]

### msf 扫描

```
use auxiliary/scanner/mongodb/mongodb_login
set rhosts xxx.xxx.xxx.xxx
set threads 20
exploit
```

![][4]

如图所示，可以看见扫描出来的服务器未授权

于是可以使用`navicat`等工具连接

![][5]

没想到还是个被黑掉的数据库，黑客要求 7 天内支付 0.1bit 币，让我们祝福这个数据库持有人

## 0x04 防御

1. 修改默认端口
2. 不要开放服务到公网

```
vim /etc/mongodb.conf
bind_ip = 127.0.0.1
```

3. 禁用 HTTP 和 REST 端口

## 0x05 使用 proxychains 代理

旧版`proxychains`使用命令

```
apt-get install proxychains -y
```

安装，版本目前为`v3.1`

新版本`proxychains ng`支持绕过本地代理功能

```
如果安装了旧版需要这两条命令下载干净
apt-get remove proxychains -y
rm /etc/proxychains.conf

git clone https://github.com/rofl0r/proxychains-ng
cd proxychains-ng
./configure --prefix=/usr --sysconfdir=/etc
make && make install
make install-config
cp proxychains-ng/src/proxychains.conf /etc/proxychains.conf
```

然后编辑配置文件，添加 sock5 代理(用小飞机)

```
vim /etc/proxychains.conf
```

`vim`在命令行状态下按`GG`跳转至末尾

删除原来的`sock4`代理

![][6]

添加指定`ip`的 1080 端口，如果是本地就`127.0.0.1`

我是树莓派使用笔记本上的小飞机，所以用的是笔记本的`ip`

![][7]

并且打开小飞机选项设置，允许来自局域网的连接：

![][8]

此时你就可以在常用命令前加上`proxychains4`语句实现代理的效果

例如，访问`google.com`:`proxychains4 curl https://www.google.com`

![][9]

` ping``google `

![][10]

### 使用 proxychains 代理 msf 遇到的问题

那么我们能不能直接代理 msf 呢？

首先，`msf`里面是能够直接设置`socks5`代理的：

```
set proxies socks5:192.168.1.7:1080
```

![][11]

但是这种方式只限于反向代理，即使用`reverse_tcp`等连接时使用的

（理解可能有误，欢迎评论区指出）

那么，我们直接使用`proxychains4 msfconsole`会怎么样呢？

![][12]

可以看到，我的老朋友`postgresql`的`5432`端口被代理给代理了

并且直接导致连不上

![][13]

而且我不使用`proxychains`而使用新版本就是看在新版本拥有代理本地的功能

继续编辑`/etc/proxychains.conf`文件

可以看到给我们举出了很多例子

![][14]

最可能用得到的就是这条`localnet 127.0.0.0/255.0.0.0`

但是我删除这条的注释之后并没有改善问题，仔细看发现`postgresql`

连接的是`localhost:5432`而不是`127.0.0.1:5432`

而且`localnet`语句直接接`localhost`会报错

**也可能是我没找到用法，有知道的大佬可以评论区告诉我**

这里有一个知识点，我们在使用`mmsfdb init`初始化`msf`的数据库时

配置文件默认生成位置是：

```
/usr/share/metasploit-framework/config/database.yml
```

![][15]

可以看到，里面连接的就是`localhost`

目前要使用`proxychains4`代理`msf`并且能让`msf`正常运行的方案

- 要么修改`postgresql`配置，让它连接`127.0.0.1`而不是`localhost`
- 要么进入`msf`手动连接`127.0.0.1`数据库

本文完。

[1]: https://cloud.tencent.com/developer/article/1555315
[2]: https://xz.aliyun.com/t/6103
[3]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_113027.png
[4]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_113310.png
[5]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_113605.png
[6]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_115536.png
[7]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_115703.png
[8]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_120112.png
[9]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_115842.png
[10]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_115938.png
[11]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_120616.png
[12]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_121007.png
[13]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_121132.png
[14]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_121217.png
[15]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200130_121559.png