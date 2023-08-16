---
title: "bossplayersCTF:1-Vulnhub Walkthrough"
categories: ["安全技术"]
tags: ["vulnhub", "靶机", "walkthrough"]
draft: false
slug: "427"
date: "2020-01-14 12:16:00"
---

[靶机地址][1]
难度：简单

## 工具及漏洞信息

- netdiscover
- nmap
- dirb
- dirsearch
- gobuster
- 命令执行
- SUID 权限 find 命令提权

## 0x00 信息收集

### 扫描靶机信息

使用`netdiscover`扫描当前网段，看见主机名是`PCS Systemtechnik GmbH`的一般就是靶机了：

![][2]

```
nmap -sS -sV -n -T4 -p- 192.168.1.8
```

- -sS: TCP 同步扫描，也称为半开放扫描
- -sV: 探测开放端口以确定服务/版本信息
- -n: 不进行 dns 解析节约时间
- -T4: 时序模板设置为 4 级
- -p-: 扫描所有端口
- -A: 启用操作系统检测，版本检测，脚本扫描和跟踪路由，-A 选项包含-sV 选项

![][3]

可以看到只开了一个`apache`服务和`ssh`

### 扫描路径

dirb 默认扫描了只显示返回状态码为 200 的地址，还是很不错的：

```
dirb http://192.168.1.8 -X .php,.txt,.zip,.html
```

![][4]

相比之下，`dirsearch`默认显示所有返回的状态码的路径，使用`-x`执行不显示的状态码：

```
python3 dirsearch.py -t 50 -e .php,.txt,.zip,.html -x 400,403,404,500,503,514,564 -u http://192.168.1.8
```

![][5]

扫描工具还有`gobuster`，字典我们可以使用`star`了 2w 多星的一个[安全字典][6]

`kali`可直接使用命令`apt install seclists -y`安装，安装完默认字典位置在

```
/usr/share/seclists
```

然后我们扫描一下

```
gobuster dir -u http://192.168.1.8 -s 200,301,302 -t 50 -w /usr/share/seclists/Discovery/Web-Content/big.txt -x .php,.txt,.html,.zip
```

![][7]

这个工具也挺好用的

## 0x01 反弹 shell

接着访问一下`robots.txt`，发现是一串`base64`编码的字符，解码后发现靶机作者在开玩笑

![][8]

访问主页，源代码最后有一行注释

![][9]

尝试使用`base64`解码三次，得到一个文件名字`workinginprogress.php`:

![][10]

访问该路径：

![][11]

提示让我们执行`ping`命令，尝试多次后发现是`cmd`命令注入：

![][12]

这也就意味着这里能执行`shell`命令

在`kali`上执行`nc`监听：

```
nc -lvp 4444
```

![][13]

在刚才的命令注入处反弹 shell:

![][14]

获取到`shell`后从`python`的`pty.spawn`获取标准 pty，从 python 命令提示符到交互式 shell

```
python -c 'import pty;pty.spawn("/bin/bash")'
```

![][15]

可以看到我们现在以当前命令注入的身份`www-data`获取到了的网站根目录下的一个`shell`

find 命令本身具有此权限。 这使我们的工作变得容易一些。

使用`find`命令查找居于 SUID 权限可执行文件，我们使用命令

```
find / -perm -u=s -type f 2>/dev/null
```

- /: 在根目录下查找
- perm: 查找指定权限的文件，/u=s 或者-u=s 参数列出系统中所有`SUID`的档案
- type: 找符合指定的文件类型的文件，-type f: 查找指定目录下所有普通文件
- 2>/dev/null: 2>部分的意思是“重定向文件通道号 2”-映射到标准错误文件通道 stderr，这是程序经常将错误写入其中的位置，/dev/null 是一种特殊字符设备，只允许向其中写入任何内容；阅读时，它不会返回任何内容，因此 2>/dev/null 让 shell 将标准错误从正在运行的程序重定向到/dev/null，从而有效地将其忽略。
- SUID: SUID (Set owner User ID up on execution) 简单来说。suid，它会出现在文件拥有者权限的执行位上，具有这种权限的文件会在其执行时，使调用者暂时获得该文件拥有者的权限。所以我们去找一个文件拥有者为 root，而且其执行位上有 s 的执行文件，那么即使我们用普通用户运行这个文件时，这个文件的执行权限就是 root
- 为什么使用 find 命令呢？原因：在 find 的后面，是可以带入命令的，而我们要的就是执行其他命令。也就是说，当我们调用 find 命令时，因为 find 命令有 s 权限，所以 find 在执行时的权限就是 root 命令，而在 find 后面的带入的命令也就是在 root 权限下执行的命令了

参考文章：

- [Unix/Linux 的 find 指令使用教學、技巧與範例整理][16]
- [Linux 配置不当提权-suid 提权][17]

![][18]

发现`/usr/bin/find`，也就是当前我们正在使用的`find`命令是具有`SUID`权限的

## 0x02 find 命令提权

尝试使用 find 命令调用/bin/sh 执行 shell

```
find . -exec /bin/sh -p \; -quit
```

- exec: 来对每一个找到的文件或目录执行特定命令。它的终止是以`;`为结束标志的，所以这句命令后面的分号是不可缺少的，考虑到各个系统中分号会有不同的意义，所以前面加反斜杠转义。
- quit: 表示命令执行完了就退出

![][19]

成功获得`root`的`shell`，查看`/root`目录下的`root.txt`文件，完成！

本文完。

参考文章：

- [bossplayersCTF 1: Vulnhub Walkthrough][20]
- [Bossplayers CTF - Walkthrough][21]
- [VulnHub 靶机系列实战教程][22]

[1]: https://www.vulnhub.com/entry/bossplayersctf-1,375/
[2]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_122237.png
[3]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_122426.png
[4]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_122700.png
[5]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_122751.png
[6]: https://github.com/danielmiessler/SecLists
[7]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_192936.png
[8]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_122857.png
[9]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_122934.png
[10]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_123011.png
[11]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_123128.png
[12]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_123208.png
[13]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_123256.png
[14]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_123317.png
[15]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_123349.png
[16]: http://blog.onepic.cc/2019/02/unix-linux-%E7%9A%84-find-%E6%8C%87%E4%BB%A4%E4%BD%BF%E7%94%A8%E6%95%99%E5%AD%B8%E3%80%81%E6%8A%80%E5%B7%A7%E8%88%87%E7%AF%84%E4%BE%8B%E6%95%B4%E7%90%86/
[17]: https://blog.csdn.net/Wu000999/article/details/100835226
[18]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_123427.png
[19]: https://img.soapffz.com/archives_img/2020/01/14/archives_20200114_123453.png
[20]: https://www.hackingarticles.in/bossplayersctf-1-vulnhub-walkthrough/
[21]: https://medium.com/infosec-adventures/bossplayers-ctf-walkthrough-83d62953d2ed
[22]: https://mp.weixin.qq.com/s/skCNWPiEPgJcHXSmsif5qQ
