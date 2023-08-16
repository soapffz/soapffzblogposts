---
title: "metasploitable2-演示常见漏洞"
categories: [ "安全技术" ]
tags: [ "漏洞利用","MSF","靶机" ]
draft: false
slug: "453"
date: "2020-01-29 19:23:00"
---

## 事情起因

**本篇文章毫无技术含量**，仅仅为演示常见漏洞使用(闲得发慌持续整理笔记中)

`metasploitable2`的话，`Rapid 7`官方很久没有维护

于是两位小哥自己设计了不能直接利用漏洞的`metasploitable3`

后面我也会演示，但是这么经典的靶机不更新了也得留下点记录

[靶机下载地址][1]

参考文章：

- [第二课 Metasploit 对 Metasploitable2 下的 SambaMS-RPC Shell 命令注入漏洞等多个漏洞进行攻击][2]

## 演示常见漏洞

Metasploitable2 漏洞列表：

1. 弱口令漏洞（如 vnc、mysql、PostgreSQL 等）
2. Samba MS-RPC Shell 命令注入漏洞
3. Vsftpd 源码包后门漏洞
4. UnreallRCd 后门漏洞
5. Linux NFS 共享目录配置漏洞
6. Java RMI SERVER 命令执行漏洞
7. Tomcat 管理台默认口令漏洞
8. root 用户弱口令漏洞（SSH 爆破）
9. Distcc 后门漏洞
10. Samba sysmlink 默认配置目录遍历漏洞
11. PHP CGI 参数注入执行漏洞
12. Druby 远程代码执行漏洞
13. Ingreslock 后门漏洞
14. Rlogin 后门漏洞

### Samba MS-RPC Shell 命令注入漏洞

> 漏洞产生原因:传递通过 MS-RPC 提供的未过滤的用户输入在调用定义的外部脚本时调用/bin/sh，在 smb.conf 中，导致允许远程命令执行。

使用`search usermap`来搜索攻击模块

![][3]

设置参数`rhosts`，即目标机的 ip

此处有个小技巧，由于后面几个漏洞都需要设置这个参数，于是我们使用`setg`

可以在同一次打开`msf`的情况里设置全局参数

![][4]

获得`shell`之后不会有回显，直接输出命令即可

![][5]

![][6]

### Vsftpd 源码包后门漏洞

> 漏洞产生原因：在特定版本的 vsftpd 服务器程序中，被人恶意植入代码，当用户名以“:)”为结尾，服务器就会在 6200 端口监听，并且能够执行任意恶意代码。

`search vsftp`搜索可用攻击模块

![][7]

设置参数攻击

![][8]

![][9]

### UnreallRCd 后门漏洞

> 漏洞产生原因：在 2009 年 11 月到 2010 年 6 月间分布于某些镜面站点的 UNreallRCd，在 DEBUG3_DOLOG_SYSTEM 宏中包含外部引入的恶意代码，远程攻击者就能够执行任意代码。使用 search unreal 来搜索攻击模块

`search unreal`搜索漏洞模块

![][10]

![][11]

本文完。

[1]: https://sourceforge.net/projects/metasploitable/files/latest/download
[2]: https://mp.weixin.qq.com/s/GwkYlxQUEKnfhkCJrS18UA
[3]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_191100.png
[4]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_191144.png
[5]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_191706.png
[6]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_191735.png
[7]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_191821.png
[8]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_191926.png
[9]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_191953.png
[10]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_192036.png
[11]: https://img.soapffz.com/archives_img/2020/01/29/archives_20200129_192120.png