---
title: "记一次打偏的spring boot接口信息泄露导致AWS s3 bucket接管"
categories: ["安全技术", "工具分享"]
tags: ["SRC", "实战", "漏洞挖掘"]
draft: false
slug: "569"
date: "2021-12-07 00:57:00"
---

# 事情起因

挖某 SRC 的资产中发现某三级子域名历史解析的 IP 为 Amazon 服务器，发现该 IP 存在 springboot 接口泄露

通过解析拿到星号加密的 AWS_SECRET_ACCESS_KEY 的明文并成功访问容器资源

但是明知道打偏还是硬着头皮提交漏洞然后被忽略的苦逼故事

# 发现接口

直接访问该 IP 为空白界面，随便在 IP 后面输入东西报错，spring boot 的经典错误界面

![][1]

于是直接扫是否存在配置错误接口，虽扫描的工具有很多，最近比较好用的是来自`winezer0`大佬的[springboot_scan][2]

当然你直接像我一样用`dirsearch`等老牌默认目录扫描工具也是可以的

这里之前快睡觉了扫完了就把结果复制到 txt 了

![][3]

可以看到存在`/env`等接口，访问`env`接口如下：

![][4]

可以看到就是标准的`env`配置信息泄露，里面全部是内网 IP，重要信息全部是星号加密

# spring boot 渗透 Tip

此处安利一波`Github`上的项目[SpringBootVulExploit][5]

> SpringBoot 相关漏洞学习资料，利用方法和技巧合集，黑盒安全评估 check list

里面非常详细，就是当你发现了 spring boot 存在一些接口时怎么渗透

_可以看到最上面两行就是我参照该项目试图用 vps 接收加密内容的记录（未成功）_

# 提取敏感信息

在返回包中搜寻了下，发现存在 AWS 相关内容，只是`AWS_ACCESS_KEY_ID`是明文

![][6]

但是`AWS_SECRET_ACCESS_KEY`是星号加密的，与此同时还有`AWS region`

这个`AWS region`后续登录是需要的，如果没有在该包中的话，也可以先查询`IP`归属地

![][7]

然后根据官方的[地区代码文档][8]中判断区域及获得对应区域名称即可

回归正文，那么要怎么获得`AWS_SECRET_ACCESS_KEY`呢

我比较青睐的方法是直接下载`heapdump`数据包从中解析

`heapdump`也就是`jvm heap`，下载的文件大小通常在`50M—500M`之间，有时候也可能会大于`2G`

上面推荐的`Github`中推荐按照[文章][9]方法使用[Eclipse Memory Analyzer][10]工具进行查询

但我实际操作过几次，并不太好找，直接下载`heapdump`，国内有大佬写过专业的分析工具[heapdump_tool][11]

使用起来也不难，配置一个`jhat`(jdk 自带的)环境变量，后面接文件名称（需解压过）

命令行选择 0 模式（不用加载所有数据，直接快速查询数据），然后直接输入你想查询的被加密的\*号值的值的名称即可

![][12]

我这里查询出来`AWS_SECRET_ACCESS_KEY`的值是一串看起来像 16 进制的值

研究了下，写了两行代码搞定

```
list = [0x45,0xxx,...,0xxx]
for i in list:
    print(chr(int("{}".format(i),0)),end="")
```

![][13]

得到一个 40 位的`AWS_SECRET_ACCESS_KEY`

# 登录 AWS S3 buckect

通过`aws`官方提供的[cli 工具][14]

通过命令行进行参数配置

- AWS_ACCESS_KEY_ID 及 AWS_SECRET_ACCESS_KEY 如实配置

- 地区上面已经说了

- 输出格式 json 即可

成功登录

![][15]

# 后话

虽然看起来没啥东西，但好歹还是接管了一个 ASW S3 Bucket，即使该域名解析的这个 IP 可能不属于该域名

但还是硬着头皮提交了，该漏洞已被忽略。

但这也是一次比较好的学习过程，所以发出来和大家交流交流。

[1]: https://img.soapffz.com/archives_img/2021/12/07/archives_20211207_011322.png
[2]: https://github.com/winezer0/springboot_scan
[3]: https://img.soapffz.com/archives_img/2021/12/07/archives_20211207_011915.png
[4]: https://img.soapffz.com/archives_img/2021/12/07/archives_20211207_012252.png
[5]: https://github.com/LandGrey/SpringBootVulExploit
[6]: https://img.soapffz.com/archives_img/2021/12/07/archives_20211207_012935.png
[7]: https://img.soapffz.com/archives_img/2021/12/07/archives_20211207_013203.png

[8]: https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/using-regions-availability-zones.html](https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
[9]: https://landgrey.me/blog/16/
[10]: https://www.eclipse.org/mat/downloads.php
[11]: https://github.com/wyzxxz/heapdump_tool
[12]: https://img.soapffz.com/archives_img/2021/12/07/archives_20211207_013739.png
[13]: https://img.soapffz.com/archives_img/2021/12/07/archives_20211207_014304.png
[14]: https://docs.aws.amazon.com/zh_cn/cli/latest/userguide/cli-chap-install.html
[15]: https://img.soapffz.com/archives_img/2021/12/07/archives_20211207_014641.png
