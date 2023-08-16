---
title: "git clone 太慢？用码云做中转站优雅提速(因为失败而变成了一篇水文)"
categories: [ "工具分享" ]
tags: [ "GitHub" ]
draft: false
slug: "24"
date: "2019-02-23 13:51:00"
---

# 事情起因

苦逼的 soapffz 的梯子搭一个挂一个，firefox 的 vpn 插件对于普通浏览境外网站足够了，但是对于下载 github 项目一点都不给力

不想费劲弄小飞机，但是下载亮哥的文章的速度实在不能忍，Github 地址：https://github.com/Micropoor/Micro8

![][1]

![][2]

于是第 n 次百度“git clone 提速”，大部分依然是推荐用中国站长等工具 ping Github 的 CDN 地址然后添加到 HOSTS 文件中，但是既麻烦又效果不明显，这次让我找到了一个脑洞比较大的同志的文章：https://blog.csdn.net/malvas/article/details/86755753

# 教程

首先在码云登陆(没有先注册)你的账号：https://gitee.com/

登陆后在右上角加号点击新建项目：

![][3]

然后什么都不用填，拉到最下面，选择导入已有仓库：

![][4]

将你需要 clone 的 Github 项目地址粘贴进去，比如：`https://github.com/Micropoor/Micro8`，然后点击创建，然后它就会自己开始拷贝：

![][5]

等待一会，时间视你要拷贝的项目的大小而定，亮神的项目 280 多 MB，大概等了 NNNNN 多分钟

然后此时下载你的 gitee 地址即可，我们看一下速度：

![][6]

emmm，速度还是很可观的，但是好像等项目创建的时间也挺长的(@(你懂的))(逃~

**提醒，这个项目我会一直保留，你们可以直接从这个项目下载亮神的专辑，我也会时不时同步**

** 19-03-07 更新：亮神已于 19-03-07 停止更新 **

下载方式：

```
git clone https://gitee.com/soapffz/Micro8.git
```

关于整理名称的方法参考文章：https://soapffz.com/python/115.html，注意把不同命名方式的文件分开再分别使用文章中的整理名字脚本

对了，此处补充一个小技巧，对于大文件夹又难得有更新那种，可以用以下方式将服务器代码更新到本地：

```
查看git 远程仓库的地址:git remote -v
更新代码本地到仓库三种方式：

方法一
git pull //将服务器最新的更改获取到本地

方法二
$git fetch origin master //从远程的origin仓库的master分支下载代码到本地的origin master
$git log -p master origin/master//比较本地的仓库和远程参考的区别
$git merge origin/master//把远程下载下来的代码合并到本地仓库，远程的和本地的合并

方法三
$git fetch origin master:temp //从远程的origin仓库的master分支下载到本地并新建一个分支temp
$git diff temp//比较master分支和temp分支的不同
$git merge temp//合并temp分支到master分支
$git branch -d temp//删除temp
```

# 插曲

正在一边刷公众号文章一边等项目创建完成(已经等了 14 分钟)的时候：

![][7]

刷到了少数派的文章：[这个安装和卸载 Windows 软件的方法超酷炫，你肯定不知道][8]，刚好是一个基于 Powershell，使用 Github 的工具-`Scoop`

然后安装要求有一条是：

> 你能 正常、快速 的访问 GitHub 并下载上面的资源

![][9]

红红火火恍恍惚惚，暴风哭泣：

![][10]

看来有一个好用的，不倒的梯子还是很重要的，此时从我创建仓库到现在已经过去 25 分钟，依然还在转圈圈，于是宣告本文推荐失败

把文章标题加了`(因为失败而变成了一篇水文)`，另外，梯子好用的同学可以试试上面说到的少数派推荐的 Windows 软件下载工具

本文完~(此时已经距离我创建仓库过去了 30 分钟，比我直接下还慢)

[1]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190223_135802.png
[2]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190223_140045.png
[3]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190223_140218.png
[4]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190223_140404.png
[5]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190223_140534.png
[6]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190223_162835.png
[7]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190223_141845.png
[8]: https://mp.weixin.qq.com/s/wrwLyNJ5Kti_YPJd4ADjTQ
[9]: https://img.soapffz.com/archives_img/2019/02/23/archives_20190223_142445.png
[10]: https://img.soapffz.com/archives_img/2019/02/23/%E6%9A%B4%E9%A3%8E%E5%93%AD%E6%B3%A3.gif