---
title: "用wpscan对wordpress站点进行渗透"
categories: ["安全技术"]
tags: ["wordpress", "渗透"]
draft: false
slug: "16"
date: "2019-01-30 11:32:00"
---

# 环境准备

## wordpress

我们用上一篇文章(传送门：[在 Ubuntu 中安装 docker 快速搭建测试环境][1])中写道的官方出品的 Docker 镜像：wpscanteam/vulnerablewordpress 快速搭建：

```
docker pull wpscanteam/vulnerablewordpress
docker run --name vulnerablewordpress -d -p 80:80 -p 3306:3306 wpscanteam/vulnerablewordpress
```

我们配置下账号密码：

![][2]

账户名是 admin，密码是 password123，标准的弱密码

然后进入网站后台，提示更新 wordpress 版本：

![][3]

顺势更新了所有的插件，主题，随便又下了两个插件：

![][4]

创建了几个用户：

![][5]

```
testadmin:123456haha:作者
soapffz:abc123456:管理员
```

## wpscan

> WPScan 是 Kali Linux 默认自带的一款漏洞扫描工具，它采用 Ruby 编写，能够扫描 WordPress 网站中的多种安全漏洞，其中包括主题漏洞、插件漏洞和 WordPress 本身的漏洞。最新版本 WPScan 的数据库中包含超过 18000 种插件漏洞和 2600 种主题漏洞，并且支持最新版本的 WordPress。值得注意的是，它不仅能够扫描类似 robots.txt 这样的敏感文件，而且还能够检测当前已启用的插件和其他功能。

Kali 中是自带 wpscan 的，但是我打开扫描就会一直卡在 Updating the Database 处，过了一会报了 timeout 错误

![][6]

Kali 也能访问工具的主页：https://wpscan.org/，但是挂了vpn也是更新不了，我们这里用Docker拉取一个wpscan，教程在wpscan的Github上也有：https://github.com/wpscanteam/wpscan

- 拉取一个 wpscan：`docker pull wpscanteam/wpscan`

![][7]

`docker run -it --rm wpscanteam/wpscan --url https://yourblog.com [options]`

后面的[options]为参数，可为空则进行默认的扫描，当然这样每次都需要执行一次 docker 命令，如果想直接进入這個 wpscan 的 docker image 上执行 wpscan 可以使用以下指令：

`docker run -it --entrypoint /bin/sh wpscanteam/wpscan`

![][8]

这个`--entrypoint /bin/sh`是什么意思呢，字面意思是用/bin/sh 作为入口，我们可以理解为用/bin/sh 即 shell 执行后面的脚本

#### 渗透站点

我们这里默认你已经进入这个 docker image 中，则可以使用 wpscan 开头的语句：

- `wpscan --url 192.168.2.18` 对整个站点进行扫描

![][9]

额，可以看到服务器和 php 版本信息，下面扫描了一些敏感目录和文件备份，还有主题和插件信息扫描

东西太多了，我们一样一样看，但是后面的每条指令扫描出的结果都会包含以下内容：

```
[+] URL: http://192.168.2.18/
[+] Started: Wed Jan 30 10:12:18 2019

Interesting Finding(s):

[+] http://192.168.2.18/
 | Interesting Entries:
 |  - Server: Apache/2.4.7 (Ubuntu)
 |  - X-Powered-By: PHP/5.5.9-1ubuntu4.24
 |  - SecretHeader: SecretValue
 |  - via: Squid 1.0.0
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] http://192.168.2.18/robots.txt
 | Found By: Robots Txt (Aggressive Detection)
 | Confidence: 100%

[+] http://192.168.2.18/searchreplacedb2.php
 | Found By: Search Replace Db2 (Aggressive Detection)
 | Confidence: 100%
 | Reference: https://interconnectit.com/products/search-and-replace-for-wordpress-databases/

[+] http://192.168.2.18/xmlrpc.php
 | Found By: Link Tag (Passive Detection)
 | Confidence: 100%
 | Confirmed By: Direct Access (Aggressive Detection), 100% confidence
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access

[+] http://192.168.2.18/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] http://192.168.2.18/wp-content/debug.log
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%
 | Reference: https://codex.wordpress.org/Debugging_in_WordPress

[+] Upload directory has listing enabled: http://192.168.2.18/wp-content/uploads/
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] WordPress version 5.0.3 identified (Latest, released on 2019-01-09).
 | Detected By: Rss Generator (Passive Detection)
 |  - http://192.168.2.18/index.php/feed/, <generator>https://wordpress.org/?v=5.0.3</generator>
 |  - http://192.168.2.18/index.php/comments/feed/, <generator>https://wordpress.org/?v=5.0.3</generator>

[+] WordPress theme in use: twentyfifteen
 | Location: http://192.168.2.18/wp-content/themes/twentyfifteen/
 | Latest Version: 2.3 (up to date)
 | Last Updated: 2019-01-09T00:00:00.000Z
 | Readme: http://192.168.2.18/wp-content/themes/twentyfifteen/readme.txt
 | Style URL: http://192.168.2.18/wp-content/themes/twentyfifteen/style.css?ver=5.0.3
 | Style Name: Twenty Fifteen
 | Style URI: https://wordpress.org/themes/twentyfifteen/
 | Description: Our 2015 default theme is clean, blog-focused, and designed for clarity. Twenty Fifteen's simple, st...
 | Author: the WordPress team
 | Author URI: https://wordpress.org/
 |
 | Detected By: Css Style (Passive Detection)
 |
 | Version: 2.3 (80% confidence)
 | Detected By: Style (Passive Detection)
 |  - http://192.168.2.18/wp-content/themes/twentyfifteen/style.css?ver=5.0.3, Match: 'Version: 2.3'
```

于是我们知道了它 wpscan 默认每次都会扫描`敏感文件`、`备份文件`、`上传目录`、`wordpress版本信息`、`主题信息`

接下来我们来扫描一些比较敏感的东西：

- `wpscan --url 192.168.2.18 --enumerate u`对用户名进行枚举

![][10]

可以看到很轻易就得到了用户名

- `wpscan --url 192.168.2.18 --enumerate t`对主题进行扫描

![][11]

得到了主题的名字和版本

- `wpscan --url 192.168.2.18 --enumerate p`对插件进行扫描

![][12]

- `wpscan --url 192.168.2.18 --enumerate vp`扫描插件中的安全漏洞

![][13]

没有插件的漏洞，同样的，扫描脆弱的主题将后面的参数 t 改为 vt 即可

- `wpscan --url 192.168.2.18 --enumerate tt`扫描 TimThumb 文件

> TimThumb 是一个非常简洁方便用于裁图的 PHP 程序，只要给他设置一些参数，它就可以生成缩略图。现在很多 WordPress 主题中，都使用 TimThumb 这个 PHP 类库进行缩略图的处理。通过 TimThumb 的漏洞很容易获得站点 root 权限。

![][14]

没有找到

- `wpscan --url 192.168.2.18 --passwords /mnt/passwd.txt --username admin –-threads 100`暴力破解 admin 密码

这里发现读不到文件:

![][15]

了解到是需要将宿主机目录挂载到镜像中的，所以我们删除这个容器重新创建一个容器：

```
exit
docker ps -a (查看wpscan这个container的id)
docker stop [id] 先停止
docker rm [id] 再删除
docker run -it -v /mnt:/tmp --entrypoint /bin/sh wpscanteam/wpscan 多加一个-v参数，使用:分割宿主机目录和镜像目录
```

![][16]

关于镜像内挂载目录的详解可以参考这篇：https://www.cnblogs.com/ivictor/p/4834864.html

然后我们爆破:

```
账号密码只有--passwords/--usernames选项，都有s，但是不但可以指定字典也可以指定单个用户名：

wpscan --url 192.168.2.18 --passwords /tmp/passwd.txt --usernames admin –-threads 100

wpscan -h帮助中的说明：
-P, --passwords FILE-PATH List of passwords to use during the password attack.
If no --username/s option supplied, user enumeration will be run.
-U, --usernames LIST List of usernames to use during the password attack.
```

开 100 个线程效果如下：

![][17]

爆破效果及速度都取决于字典和线程的大小，爆破 admin 密码的效果如下：

![][18]

![][19]

密码在 16878 行，花费了 35 分 20 秒，速度，emmm，**爆破是世界上最没有效率的办法**

其他的参数可以使用 wpscan -h 来查看

- wpscan 的 Github 地址：https://github.com/wpscanteam/wpscan#wpscan-arguments
- GitHub 的 Readme.md 的中文翻译：https://www.test404.com/post-1627.html?wafcloud=1

利用 searchreplacedb2.php 修改邮箱重置密码拿下管理员账号

这是一个用于 WordPress 网站更换域名之后批量替换数据库内容的工具。但是用了两下之后可以看出，它只能替换，并没有找到查询数据的方法。

- https://wpshout.com/links/searchreplacedb2/
- https://github.com/jmandala/searchreplacedb2

另外，searchreplacedb2.php 会自动读取 wp-config.php，然后返回的表单里面也包含数据库用户名和密码。存在一个遗留后门 searchreplacedb2.php，可以利用它修改管理员 admin 预留的邮箱，点击忘记密码发送重置密码链接，然后重置密码。

这个文件的利用方式参考文章：https://blog.csdn.net/t91zzh5f/article/details/55805438

#### 防范措施

1.怎么防止 wordpress 网站被人暴力破解管理员密码呢?

防止暴力破解的最好方式是限制一个 IP 地址的尝试登录次数。WordPress 有 n 多插件可以实现这个功能，比如：

- Login Security Solution
- Brute Force Login Protection
- 也可以写一个脚本防止爆出个人密码

  2.如何防范扫描插件、主题、TimThumb 文件

使用 Block Bad Queries (BBQ)插件，就可以屏蔽和禁止这类扫描

[1]: https://www.soapffz.com/sec/99.html
[2]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_115811.png
[3]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_163702.png
[4]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_164657.png
[5]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_165203.png
[6]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_113339.png
[7]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_115959.png
[8]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_165546.png
[9]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_171028.png
[10]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_180753.png
[11]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_180956.png
[12]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_181109.png
[13]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_181356.png
[14]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_181153.png
[15]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_194731.png
[16]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_195303.png
[17]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_200018.png
[18]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_204657.png
[19]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_204543.png
