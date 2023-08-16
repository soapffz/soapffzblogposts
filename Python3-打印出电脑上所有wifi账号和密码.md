---
title: "Python3 打印出电脑上所有wifi账号和密码"
categories: [ "Python" ]
tags: [ "Python","无线WiFi" ]
draft: false
slug: "4"
date: "2018-12-15 22:35:00"
---

#### 原理

##### cmd 查询本地 wifi 配置

在 cmd 执行命令`netsh wlan show profiles`：

![][1]

能显示出此电脑上所有的 Wlan 配置文件，我们要查看其中一个的密码，指定 name=wlan 名(也就是 SSID) key=clear 即可，
`netsh wlan show profiles name=连了是SB key=clear`

![][2]

##### Python 的 os.popen()函数用 cmd 执行传入参数

Python 中有一个 os 文件/目录库，其中有一个函数叫做 os，其中一条指令为 os.popen，能够用于从一个命令打开一个管道

os.popen 介绍:[python os.popen 方法 | 菜鸟教程][3]

也就是这条命令能够用 cmd 执行传入的字符串，比如`os.popen('dir').read()`
![][4]

这就是用到的所有基本知识

#### 代码讲解

- 首先肯定要导入库`import os`

- 然后我们用 os.popen()函数先查询总的 wifi 配置：

```
cmd_get_allpfs = ('netsh wlan show profiles')
with os.popen(cmd_get_allpfs) as f:
    SSID_list = []
    for line in f:
        if'所有用户配置文件 :' in line:
            line = line.strip().split(":")[1]
            SSID_list.append(line)
```

- 如果返回的内容行中含有'所有用户配置文件 :'这个字样，就把这一行用:分割，将后面的部分，也就是 wifi 名，存储到 wifi 名列表 SSID_list 中，然后我们再挨条执行密码查询语句并打印出来：

```
for SSID in SSID_list:
    cmd_get_evepf = ('netsh wlan show profiles name={} key=clear'.format(SSID))
    with os.popen(cmd_get_evepf) as r:
        evepf = r.read()
        print(evepf)
```

- 将列表中的 SSID 挨条格式化传入查询语句，然后打印出查询内容，效果如下：
  ![][5]

当然，如果你只想简单地获取 SSID 和密码，比如

```
SSID_name1:passwod1
SSID_name2:passwod2
```

这样的，简单改一下就好了，以下为获取`SSID:password`的全部代码：

```
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 打印出电脑上所有的wifi账号：密码
@time:2018-12-15
'''

import os

cmd_get_allpfs = ('netsh wlan show profiles')
with os.popen(cmd_get_allpfs) as f:
    SSID_list = []
    for line in f:
        if'所有用户配置文件 :' in line:
            line = line.strip().split(":")[1]
            SSID_list.append(line)

PASS_list = []

for SSID in SSID_list:
    cmd_get_evepf = ('netsh wlan show profiles name={} key=clear'.format(SSID))
    with os.popen(cmd_get_evepf) as r:
        for line in r:
            if'关键内容'in line:
                line = line.strip().split(":")[1]
                PASS_list.append(line)

for i in range(len(SSID_list)):
    print("{}:{}".format(SSID_list[i], PASS_list[i]))
```

- 效果如下：

![][6]

[1]: https://img.soapffz.com/archives_img/2018/12/15/archives_20181215_224049.png
[2]: https://img.soapffz.com/archives_img/2018/12/15/archives_20181215_224528.png
[3]: http://www.runoob.com/python/os-popen.html
[4]: https://img.soapffz.com/archives_img/2018/12/15/archives_20181215_225143.png
[5]: https://img.soapffz.com/archives_img/2018/12/15/archives_20181215_230539.png
[6]: https://img.soapffz.com/archives_img/2018/12/15/archives_20181215_232834.png