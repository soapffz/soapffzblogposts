---
title: "一道CTF的SQL注入题"
categories: ["安全技术", "CTF"]
tags: ["SQL"]
draft: false
slug: "529"
date: "2020-03-19 15:24:00"
---

## 事情起因

来自某内测靶场，未开放注册，跟随在字节脉搏的`lation`老哥复现一遍，学习姿势，[靶场地址][1]

## 探寻注入方式

打开靶场长这样：

![][2]

看起来一个“简单”的登录框，`burp`拦截发送`reapter`开始探测

![][3]

看起来很正常，只有`username`和`passwd`两个字段，先尝试万能密码账号

![][4]

登录失败，这里有个小技巧，建议`burp`改参数时选中自己添加的部分`ctrl+U`过一次`URL`编码

`admin`加单引号也没啥反应，后面加`and 1=1`和`and 1=2`也没啥反应

尝试`passwd`字段加单引号

![][5]

也没啥反应，尝试报错注入：

![][6]

也没啥反应，尝试宽字节注入：

![][7]

报错了，尝试闭合报错语句：

![][8]

经测试，除了`--+`还有`#`和`-- -`均能闭合

## 注入数据

老规矩，先查询列数：

![][9]

报错了，可以看到报错处提示`near 'der by 3`，说明我们的`or`被吃了，尝试双写绕过：

![][10]

![][11]

`order by 3`没问题，`order by 4`报错了，`union select`查看回显字段：

![][12]

直接回显`登录成功，flag在flag1表中，列名为key1`(我这里显示有点重叠)，直接查值

![][13]

发现没变化

> 在报错注入的时候需有对`information_schema库`有读取权限

> 无`information_schema`库读取权限，需同时猜解列名和表名（较难）

那我们就使用之前的报错注入来查询数据：

![][14]

注意，此处在`%df%27`后面还有一个`%`

参考文章：

- [一道简单、有趣的 SQL 注入题][15]

本文完。

[1]: http://dcnctf.com:2020/sqli/index.php
[2]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_153332.png
[3]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_153524.png
[4]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_153831.png
[5]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_154130.png
[6]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_154630.png
[7]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_154830.png
[8]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_154941.png
[9]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_155135.png
[10]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_155251.png
[11]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_155323.png
[12]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_155422.png
[13]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_160421.png
[14]: https://img.soapffz.com/archives_img/2020/03/19/archives_20200319_161335.png
[15]: https://mp.weixin.qq.com/s/ZO5LXeCN-I6dodRZYsbUrQ
