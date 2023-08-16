---
title: "Cl0neMast3r--GitHub的克隆工具"
categories: [ "工具分享" ]
tags: [ "GitHub" ]
draft: false
slug: "26"
date: "2019-02-15 16:27:00"
---

# 起因

在 freebuf 搜索 bettercap 的相关文章时看到的，感觉可能有点用

原文链接：https://www.freebuf.com/sectool/164805.html

GitHub 地址：https://github.com/Abdulraheem30042/Cl0neMast3r

# 环境要求

- Python 2.7.
- Requests: pip install requests
- BeautifulSoup4: pip install beautifulsoup4

# 安装

```
git clone https://github.com/Abdulraheem30042/Cl0neMast3r.git
cd Cl0neMast3r/
pip install -r requirements.txt
```

![][1]

# 运行

`python Cl0neMast3r.py`

主界面：

![][2]

以 MITM 攻击测试框架 bettercap 为例，我们首先进行工具的查找和下载

选项 F 在 Github 上查找，用工具名查找，找到了 67 个项目：

![][3]

我们显示前 5 个看一下：

![][4]

我们可以看到返回的结果中显示了：

- 作者
- URl 地址
- 可用性
- 相关描述

我们选择 Tool Number 为 2 进行下载，提示添加完成，并提示按 M 键返回主菜单：

![][5]

我们来看一下更新功能，我们选择的是更新已有工具：

![][6]

S 选项能查看现有工具的状态：

![][7]

如果工具太多可以也可直接备份到 HTML 文件中，这里备份的其实是 GitHub 的相关链接：

![][8]

工具就分享到这。

[1]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_163312.png
[2]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_163435.png
[3]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_163742.png
[4]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_163839.png
[5]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_164134.png
[6]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_164456.png
[7]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_164608.png
[8]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_164853.png