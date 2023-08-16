---
title: "Python3 - 递归查找多层目录中指定类型文件"
categories: [ "Python" ]
tags: [ "Python" ]
draft: false
slug: "8"
date: "2019-01-06 18:17:00"
---

##### 这个代码是为了 Hack.lu CTF 2017-Flatscience-writeup 补上的，[传送门][1]

```
# !/usr/bin/python
# -  *  - coding:utf-8 -  *  -
'''
@author: soapffz
@fucntion: 递归查找多层目录中指定类型文件
@time: 2019-01-06
'''

import os
import shutil

src_dir = r"C:\Users\soapffz\Desktop\dir"  # 注意复制目录路径的时候最前面可能有个看不见的字符
to_dir = os.path.join(os.path.expanduser("~") + "\\" +
                      "Desktop" + "\\" + "to_dir")  # 生成的文件夹放在了桌面
os.mkdir(to_dir)


def search_file(path):
    for item in os.listdir(path):
        subFile = os.path.join(path + "\\" + item)
        if os.path.isdir(subFile):
            search_file(subFile)
        else:
            if os.path.splitext(subFile)[1] == ".pdf":
                shutil.copy(subFile, to_dir)


if __name__ == "__main__":
    search_file(src_dir)
```

##### 效果如下：

![][2]

[1]: https://soapffz.com/sec/ctf/6.html
[2]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_185741.png