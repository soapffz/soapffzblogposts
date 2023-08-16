---
title: "赛博地球杯工业互联网安全大赛-大量设备报表不见(签道题)-writeup"
categories: ["CTF"]
tags: ["CTF", "CTF writeup"]
draft: false
slug: "13"
date: "2019-01-06 23:46:00"
---

- 为什么要写已经结束很久的题的 writeup：因为在做某 CTF 训练平台的题

首先打开链接，是一个工控管理系统：

![][1]

把左边的按钮全部点一遍，只有报表中心能进去：

![][2]

选个时间没啥反应，左下角还提醒你这是送分题，emmm，看到链接是 id=1，遂想到跑一跑 id 试一下

burp 抓包，send to intruder，并设置 Payload type 为 Numbers：

![][3]

从 1 到 5000 逐渐递增，每次加 1，线程设置为 999，设置太小跑到一半就很难动了：

![][4]

然后开始跑包，跑完之后其实就可以看到 2333 这个 id 是有问题的：

![][5]

直接让 id=2333，得到 flag：

![][6]

我们这里还有一种办法，可以使用一个小工具：search and replace，[点我去下载][7]，在抓完包之后将服务器返回的数据保存下来：

![][8]

然后用工具打开并搜索 flag，将文件过滤设置为`*.*`，然后搜索即可得到 flag：

![][9]

[1]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_233421.png
[2]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190107_002713.png
[3]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_235110.png
[4]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190107_000446.png
[5]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190107_001920.png
[6]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190107_002555.png
[7]: https://www.5down.net/soft/search-and-replace.html
[8]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190107_002111.png
[9]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190107_002320.png
