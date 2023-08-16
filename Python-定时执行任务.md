---
title: "Python-定时执行任务"
categories: [ "Python" ]
tags: [ "Python" ]
draft: false
slug: "235"
date: "2019-06-16 17:14:00"
---

# 起因

最近在写自动签到脚本，想挂在服务器上每天 12 点执行，由此牵扯出一大堆类似的定时问题

本篇解答一下

# 每隔 xx 秒执行一次程序

这是基础，用`time.sleep`即可做到，直接上程序：

```
# 每5秒打印一次
from datetime import datetime
from time import sleep


def print_message():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("https://soapffz.com")


while True:
    print_message()
    sleep(5)
```

![][1]

由此可以尝试我们的目标：

```
from datetime import datetime
from time import sleep


def print_message():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("https://soapffz.com")


while True:
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            break
        sleep(20)
    print_message()
```

虽然简单粗暴，但是这个`while`循环将会一直占用`CPU`资源，一般不建议使用

# threading.Timer 定时器

上面一种太过于暴力，我们换一种优雅的方法

`threading`中有个`Timer`类。它会新启动一个线程来执行定时任务，所以它是非阻塞函式。

如果你有使用多线程的话，需要关心线程安全问题。那么你可以选使用 threading.Timer 模块。

`Timer()`函数可接受三个参数：

```
Timer(10, task, ()).start()
延迟多长时间执行任务(单位: 秒)
要执行的任务, 即函数
调用函数的参数(tuple)
```

## 延迟 xx 秒执行程序，只一次

```
from datetime import datetime
from time import sleep
from threading import Timer


def print_message():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("https://soapffz.com")


Timer(10, print_message).start()
```

![][2]

## 每隔 xx 秒执行一次程序，一直执行

其实就是把`Timer()`语句移到执行的函数里

```
from datetime import datetime
from time import sleep
from threading import Timer


def print_message():
    Timer(10, print_message).start()
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("https://soapffz.com")


print_message()
```

![][3]

同理，需要每隔 24 小时(不论起始时间)，只需要把`Timer`函数中的时间改为 86400 即可

# schedule 模块定时执行任务

官方文档：https://schedule.readthedocs.io/en/stable/

这是一个轻量级的定时任务调度的库，我们来看几个例子：

```
from datetime import datetime
from time import sleep
import schedule


def print_message():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("https://soapffz.com")

schedule.every(15).seconds.do(print_message)
schedule.every().minutes.do(print_message)
schedule.every().hour.do(print_message)
schedule.every().day.at("10:30").do(print_message)
schedule.every(5).to(10).days.do(print_message)
schedule.every().wednesday.at("13:15").do(print_message)

while True:
    schedule.run_pending()
    sleep(1)
```

上面的意思就是：

```
每隔15秒执行一次任务
每隔1分钟执行一次任务
每隔1小时执行一次任务
每天的10:30执行一次任务
每隔5到10天执行一次任务
每周一的这个时候执行一次任务
每周三13:15执行一次任务
run_pending：运行所有可以运行的任务
```

![][4]

注意到运行结果中有一次重复打印了，不知道什么原因~可以在留言区探讨

> schedule.run_pending()是个什么东西呢——

> schedule 其实就只是个定时器。在 while True 死循环中，schedule.run_pending()是保持 schedule 一直运行，去查询上面那一堆的任务，在任务中，就可以设置不同的时间去运行。跟 linux 中设置 crontab 定时任务是类似的。

> 所以，schedule 有一定的局限性，所以只能用来执行一些小型的定时任务，它的局限性在哪呢——

> 1.需要定时运行的函数 job 不应当是死循环类型的，也就是说，这个线程应该有一个执行完毕的出口。一是因为线程万一僵死，会是非常棘手的问题；二是下一次定时任务还会开启一个新的线程，执行次数多了就会演变成灾难。

> 2.如果 schedule 的时间间隔设置得比 job 执行的时间短，一样会线程堆积形成灾难，也就是说，我 job 的执行时间是 1 个小时，但是我定时任务设置的是 5 分钟一次，那就会一直堆积线程。

另外还有一个库`sched.scheduler`，用法和`Timer()`差不多，有兴趣的可以自己了解一下

# 总结

最后，我使用了`datetime`+`sleep`搭配的第一种方法和`schedule`的第三种方法做对比

服务器配置：1 核心 CPU，1838MB 内存

第一种在平时的消耗如下：

![][5]

第三种在平时的消耗如下：

![][6]

虽然看起来后面一种好像平时更占优势，但是当时间到达指定时间的时候

前者很稳定，也不占什么 CPU，后者不知道发什么疯，占了所有的内存和 CPU，给我推送了超多消息

但是我看了下程序也没问题，所以我个人还是建议使用前者，稍微稳妥一点，双重循环还是很致命的。

就酱，本文完。

参考文章：

- [Python 定时任务（上）][7]
- [python 定时器，每天凌晨 3 点执行方法][8]
- [Python3 学习（八）：使用 schedule 模块定时执行任务][9]

[1]: https://img.soapffz.com/archives_img/2019/06/16/archives_20190616_172107.png
[2]: https://img.soapffz.com/archives_img/2019/06/16/archives_20190616_180713.png
[3]: https://img.soapffz.com/archives_img/2019/06/16/archives_20190616_181000.png
[4]: https://img.soapffz.com/archives_img/2019/06/16/archives_20190616_190029.png
[5]: https://img.soapffz.com/archives_img/2019/06/16/archives_20190616_195041.png
[6]: https://img.soapffz.com/archives_img/2019/06/16/archives_20190616_195525.png
[7]: https://www.jianshu.com/p/d04bd534b219
[8]: https://blog.csdn.net/u011311291/article/details/80016859
[9]: https://blog.csdn.net/liao392781/article/details/80521194