---
title: "[HTB]Hack The Box介绍"
categories: ["安全技术"]
tags: ["靶机", "htb"]
draft: false
slug: "513"
date: "2020-02-18 16:59:00"
---

## 事情起因

[VulnHub][1]和[HTB][2]是靶机方面比较著名的两个靶场

本篇将介绍 HTB 的常用操作以及邀请码的获取

## 邀请码的获取

在官网点击`join`之后会跳转到输入邀请码界面，需要输入邀请码才能进入

![][3]

```
curl -X POST https://www.hackthebox.eu/api/invite/generate
echo 'code的内容' | base64 -d
```

![][4]

输入即可注册登录，登陆后主界面如图所示：

![][5]

![][6]

各部件都是字面意思。

参考文章：

- [Hack The Box 获取邀请码][7]
- [【HTB 靶场系列】如何获得邀请码及如何跟 HTB 建立连接][8]

[1]: https://www.vulnhub.com/
[2]: https://www.hackthebox.eu/
[3]: https://img.soapffz.com/archives_img/2020/02/18/archives_20200218_170222.png
[4]: https://img.soapffz.com/archives_img/2020/02/18/archives_20200218_170620.png
[5]: https://img.soapffz.com/archives_img/2020/02/18/archives_20200218_172235.png
[6]: https://img.soapffz.com/archives_img/2020/02/18/archives_20200218_175152.png
[7]: https://www.cnblogs.com/sym945/p/11767098.html
[8]: https://mp.weixin.qq.com/s/1P5tI9jmRETZD_1yrqZImQ
