---
title: "Sh00t：一个渗透测试管理工具"
categories: [ "工具分享" ]
tags: [ "渗透","信息收集","渗透工具" ]
draft: false
slug: "25"
date: "2019-03-14 20:00:00"
---

** 文章参考：[Sh00t：一个渗透测试管理工具][1] **

项目地址：https://github.com/pavanw3b/sh00t

我同步过来了：https://gitee.com/soapffz/sh00t

# 工具作用

** 一句话总结:根据标准的渗透测试准则将你需要渗透的每一项任务给你列出来，当你完成时可以勾选你已完成，起到一个代办清单的作用 **

参考 GitHub 项目首页的翻译：

> Security Testing is not as simple as right click > Scan. It's messy, a tough game. What if you had missed to test just that one thing and had to regret later? Sh00t is a highly customizable, intelligent platform that understands the life of bug hunters and emphasizes on manual security testing.

> 安全测试不像右键单击>扫描那么简单。这是一个混乱，一场艰难的比赛。如果你错过了测试那一件事并且后来不得不后悔怎么办？ Sh00t 是一个高度可定制的智能平台，可以了解漏洞猎手的生活，并强调手动安全测试。

也就是说这个工具的作用也就类似于一个记事本，是帮你列出你进行渗透测试所需要的事项并且帮你生成报告的，并不是一个右键 -> 开始渗透的“神器”

# 工具安装

- 安装环境需求

** 我的环境：Win10+Anaconda，其他环境的可以去看看 GitHub **

\*附：[Python 入门之环境配置篇 -Anaconda 及 Pycharm 及格式化工具 Black 一把梭 ][2]

```
git clone https://gitee.com/soapffz/sh00t.git
cd sh00t
pip install -r requirements.txt
```

- 设置数据库：

```
python manage.py migrate
```

![][3]

- 创建用户帐户：

```
python manage.py createsuperuser
```

并按照 UI 创建帐户

![][4]

# 工具使用

## 启动：

```
python manage.py runserver
```

访问：http://127.0.0.1:8000/即可：

![][5]

使用之前在设置中创建的用户凭据登录，主界面如图所示：

![][6]

## 它是如何工作的？

> 首先创建一个新的评估(Assessment)。选择您要测试的方法。 今天有 330 个测试用例，分为 86 个标志，属于 13 个模块，参考“Web 应用程序黑客手册”测试方法创建。 模块和标志可以精心挑选和定制。 使用 Flags 创建评估后，现在测试人员必须手动测试它们(Sh0t)，或者在扫描仪，工具的帮助下进行半自动测试，或者根据需要进行测试，在完成时将其标记为“完成”。 在执行评估时，我们经常会提供特定于应用程序中某些场景的自定义测试用例。可以在任何时间轻松创建新标志。每当确认一个 Flag 是一个有效的 bug 时，就可以创建一个 Sh0t。 可以选择最匹配的错误模板，sh00t 将根据所选模板自动填充错误报告。

## 实例演示

我这里以访问我自己的站点为例，讲一下工具的使用

### 创建项目

就在 Projects 那创建一个新的就好了

### 配置评定(Assessments)

然后创建一个新的 Assessments，参数解释如下(请夸我谢谢),WAHH(我也不知道是啥)选项如下：

![][7]

OWASP(这个大家都听过了吧)配置如下：

![][8]

我这里都全选了看下效果

### 配置 Sh0t

添加你所需要渗透的站点(或内容)，然后选定一个安全等级：

![][9]

到此为止，你已经做完了你的所有准备工作，然后你就可以查看你的任务清单了：

![][10]

P1 等级也就才 174 多个 flag 而已(手动狗头)：

![][11]

**一句话：这是个任务清单!**

[1]: https://www.freebuf.com/sectool/197395.html
[2]: https://www.soapffz.com/python/5.html
[3]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_194952.png
[4]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_195011.png
[5]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_195302.png
[6]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_195341.png
[7]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_203143.png
[8]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_203658.png
[9]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_204426.png
[10]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_205415.png
[11]: https://img.soapffz.com/archives_img/2019/03/14/archives_20190314_205459.png