---
title: "网站nginx访问日志分析"
categories: ["安全技术"]
tags: ["webshell", "渗透", "日志分析"]
draft: false
slug: "247"
date: "2019-06-28 17:49:00"
---

# 起因

(正在复习三门考试的我又来摸鱼写文章了而且还不是基础文章的更新,哦~这该死的地心引力)

复习的时候带电脑真的容易摸鱼。。正在摸鱼浏览我的为之笔记保存的文章时

看到了一篇保存了很久的写的很好的日志分析文章：[shell 在手分析服务器日志不愁?][1]

今天根据这篇文章简单地分析下网站访问日志和服务器访问日志，看看网站安全防护有哪些做得不够的地方

# 分析

## 下载日志

由于我用`MobaXterm`连接服务器的`shell`时，发现一会不操作就直接掉线了，干脆把日志下载回来用`Ubuntu`分析

在这里顺便推荐下`MobaXterm`这个`Windows`全能终端神器，我的入坑文章：[Windows 全能终端神器—MobaXterm][2]

本来想在工具分享目录写一篇关于这个的文章，但是自己也没那么多的服务，大家看看上面的入坑文章就好

当然像我这种小白使用的就是`吾爱破解`的“汉化版”，现在用的版本是`hx77890`大佬汉化的`v11.1 Bulid 3860`

[点我去原帖下载][3]，有能力的话还是支持一下[正版][4]，汉化版长这个亚子：

![][5]

网站的访问日志一般在`/www/wwwlogs`目录下，打开目录：

![][6]

可以看到一个以网站名字命名的`log`和一个`access.log`，前者是网站的日志，后者是访问日志

网站日志大概长这样：

![][7]

## 分析

(命令行分析的参数的解释后面会补上)

日志下载好放到`ubuntu`中：

![][8]

开始分析网站的日志

查看有多少个 ip 访问：

```
awk '{print $1}' soapffz.com.log|sort|uniq|wc -l
```

![][9]

将每个 IP 访问的页面数进行从小到大排序并查看访问最多的 30 个 ip：

```
awk '{++S[$1]} END {for (a in S) print S[a],a}' soapffz.com.log | sort -n | tail -n 30
```

![][10]

使用我上一篇文章：`Python--批量查询ip地址`中的脚本，查询如下：

![][11]

当然看访问量最大的`ip`不止这一种方法：

```
awk '{print $1}' soapffz.com.log |sort -n -r |uniq -c | sort -n -r | head -20
```

![][12]

查看某一个`ip`访问了哪些页面，这里就选除了腾讯云等企业之外访问最多的`ip`：

```
grep ^140.207.120.100 soapffz.com.log| awk '{print $1,$7}'
```

![][13]

可以看到这位来自上海的大兄弟尝试访问了`/wp-login.php`和`/store/wp-includes/wlwmanifest.xml`

等常见`wordpress`的敏感页面，而且只访问了这两个，看起来不像扫描器扫描的

查看访问次数最多的 20 个文件或页面：

```
cat soapffz.com.log|awk '{print $11}'|sort|uniq -c|sort -nr | head -20
```

![][14]

`soapffz.com.log`看得差不多了，来看看`access.log`

查看访问最高的`ip`：

![][15]

查看`ip`的地址：

![][16]

查看访问次数第一的`ip`访问了哪些端口：

![][17]

幸好我打开日志看了一眼，前面说的访问的页面只包括`网址：端口`后面的内容，这个`59.36.132.140`

来自`广东省东莞市 电信`的大兄弟一直在爆破我的`888`端口啊，`soapffz.com.log`重新看了一下没发现这个问题

`888`端口是`phpmyadmin`端口，可能是前面我自己`po`出端口来被盯上了吧

既然这位大兄弟喜欢爆破，那我就(大 gif 预警)：

![][18]

::quyin:1huaji::

加油，大兄弟！

# 总结

简单总结一下，只开自己需要的端口

如果是常见必须开的端口，那也要用安全措施，以下为我做的措施：

- 安装完博客框架后，删除`install`文件夹及其他配置文件
- 关闭或删除不需要的端口
- SSH 使用私钥连接
- 宝塔等面板使用安全入口登录，修改登录路径
- 使用腾讯云等的 web 安全防护工具
- 检测网站异常访问`ip`并自动封禁

本文完。

[1]: https://segmentfault.com/a/1190000009745139
[2]: https://www.isharebest.com/mobaxterm.htm
[3]: https://www.52pojie.cn/thread-874448-1-1.html
[4]: https://mobaxterm.mobatek.net/download.html
[5]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190628_160436.png
[6]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190628_161739.png
[7]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190628_162759.png
[8]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190628_163049.png
[9]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_095903.png
[10]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_100401.png
[11]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_094405.png
[12]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_100531.png
[13]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_095307.png
[14]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_095716.png
[15]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_100244.png
[16]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_100754.png
[17]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_101521.png
[18]: https://img.soapffz.com/archives_img/2019/06/28/archives_20190629_105209.gif
