---
title: "内网-DNS欺骗和ARP欺骗详解"
categories: ["安全技术"]
tags: ["内网", "DNS", "ARP", "Kali"]
draft: false
slug: "23"
date: "2019-02-15 11:46:00"
---

本文目录：

- 事情起因
- 
- DNS 欺骗
- 原理
- 实战
- 用 Ettercap 实现恶搞
- 用 SET+Ettercap 实现钓鱼
- Bettercap
- Cain & Abel
- ARP 欺骗
- 原理
- 实战
- arpspoof
- ettercap
- bettercap
- Cain & Abel

# 事情起因

为了查看隔壁妹子或者兄 dei 在看啥，或者是提醒隔壁小声一点

参考文章：

- [新手渗透测试训练营——欺骗与嗅探][1]
- [技术讨论 | 利用 SET 和 Ettercap 实现内网钓鱼获取帐号密码][2]
- [揭秘 Bettercap，教你如何使用这款中间人工具！][3]
- [使用 Bettercap-2.6 进行 ARP 欺骗尝试][4]
- [内网环境实验学习笔记][5]

# 

- Kali：192.168.1.107，用来攻击
- Win7：192.168.1.106，用来被攻击

两台机子都是通过桥接网卡上网

使用工具：

- Ettercap
- Bettercap
- `Dsniff`工具套件中的`arpspoof`和`driftnet`

# DNS 欺骗

## 原理

- DNS(域名系统)是什么？

> 域名系统（英文：Domain Name System，缩写：DNS）是互联网的一项服务。它作为将域名和 IP 地址相互映射的一个分布式数据库，能够使人更方便地访问互联网。

当我们访问一个域名，比如`soapffz.com`时，浏览器会去请求 DNS 服务器，通过 DNS 服务器获取域名对应的 ip`140.143.2.176`(我的服务器 ip 开启了防 ping 功能)

- DNS 欺骗是什么?

> DNS 欺骗就是攻击者冒充域名服务器的一种欺骗行为。 原理：如果可以冒充域名服务器，然后把查询的 IP 地址设为攻击者的 IP 地址，这样的话，用户上网就只能看到攻击者的主页，而不是用户想要取得的网站的主页了，这就是 DNS 欺骗的基本原理。DNS 欺骗其实并不是真的“黑掉”了对方的网站，而是冒名顶替、招摇撞骗罢了。

- 所以我们经常听到的运营商的 DNS 劫持，就是运营商修改了你的网络的默认 DNS 服务器中的网址对应的 ip 地址，就会出现弹窗广告等现象，我们阻止运营商 DNS 劫持的有效办法：修改自己的 DNS 服务器为公共 DNS 地址，如 114.114.114.114 等

关于 DNS 解析更详细的内容可参考：[理解 DNS 记录以及在渗透测试中的简单应用][6]

那么我们可以用 DNS 欺骗来实现什么功能呢：**恶搞或者钓鱼**

## 实战

在 Linux 下实现 DNS 欺骗可用`Ettercap`(其实也用到了一部分 arp 欺骗)，可配合`SET`进行钓鱼，也可使用`bettercap`

在 Windows 下可使用`Cain & Abel`

### 用 Ettercap 实现恶搞

首先我们使用强大的中间人攻击工具：`Ettercap`

1.编辑 ettercap 的 dns 文件：

```
vim /etc/ettercap/etter.dns
```

如果是恶搞，不想让对方访问任何界面，那就让所有网址都指向一个 ip，我们这里为了起到善意的提醒作用，让所有的 ip 指向我的电脑：

![][7]

2.开一个 apache2 服务

把 apache 默认配置界面：`/var/www/html/index.html`备份之后

把里面的内容替换为自己的内容：

```
<HTML>

<HEAD>
    <meta http-equiv="content-type" content="txt/html; charset=utf-8" />
    <TITLE>大兄dei你好呀</TITLE>

<BODY>
    <p>是不是很惊喜呀！</p>
    <p>我就是过来和你打个招呼</p>
    <p>没有恶意</p>
    <p>有空一起撸啊撸啊</p>
    <p>我的网站：https://soapffz.com/</p>
</BODY>
</HEAD>

</HTML>
```

![][8]

然后重启 apache2 服务，打开看一眼是不是我们的界面：

![][9]

OK，没毛病

3.开始欺骗

我们先使用图形化界面：`ettercap -G`，选择 Unified sniffing 以中间人的方式进行嗅探：

![][10]

选择自己对应的网卡进入，然后我们对局域网进行扫描，通过 Host list 打开主机名单：

![][11]

将网关添加到目标 1，将攻击目标添加到目标 2：

![][12]

接下来在 Mitm（中间人攻击）中选择 ARP poisoning（arp 欺骗）：

![][13]

勾选远程嗅探链接，确定：

![][14]

在插件中选择 dns_spoof：

![][15]

双击，然后前面会出现一个\*号，最后点击 Start sniffing，开始我们的 dns 欺骗攻击：

![][16]

这样我们的攻击目标打开所有网页时都会显示我们自定义的页面：

![][17]

但是这样的攻击也有弊端，比如我们不能欺骗 https 协议的网址还有容易暴露我们的 ip：

![][18]

我们也可以用命令来操作 ettercap：开启 IP 转发，设计欺骗网页等步骤和图形界面是一样的。但是借助命令行，只需要一条命令，就可以执行上述复杂的操作过程：

```
ettercap -TqM ARP:remote -P dns_spoof /192.168.1.1// /192.168.1.107//
```

参数解释：

- -i：指定网卡，一般默认为 eth0
- -T：仅使用文本 GUI
- -q：启动安静模式（不回显的意思）
- -M：执行中间人攻击
- ARP:remote：使用远程嗅探
- -P：指定插件
- 后面的两个位置，第一个为目标 1，第二个为目标 2，都使用/ //包括着

![][19]

上面介绍的恶搞的部分，那么如何实现钓鱼呢，只需要在/etc/ettercap/etter.dns 文件中把受害者可能访问的网页的 ip 地址设置为你的即可

那么我们还需要自己写一个 google 界面或者百度界面，显得很麻烦

### 用 SET+Ettercap 实现钓鱼

当然这里只是讲到 Ettercap 用这个例子，还有其他强大的钓鱼工具例如：[BlackEye][20]

此处我们引入**社会工程学工具集**：Social-Engineer Toolkit，后面简称 SET

它和 Kali 应用程序收藏中的`Social Engineering Tools`不是同一个东西哦：

![][21]

顾名思义，SET 主要用来进行社工攻击，包括钓鱼网站，无线 AP 攻击，QRCode 攻击等等。

在本次实验中，SET 主要用来搭建钓鱼网站，以及监听 HTTP 请求中发送的帐号密码。

其他的使用方法可参考文章：[社会工程学工具集 Social-Engineer Toolkit 基础使用教程][22]

使用`setoolkit`命令进入，以下开始偷懒，都是复制[这篇文章][23]的

```
 Select from the menu:
   1) Social-Engineering Attacks  // 选择1，社会工程学攻击
   2) Penetration Testing (Fast-Track)
   3) Third Party Modules
   4) Update the Social-Engineer Toolkit
   5) Update SET configuration
   6) Help, Credits, and About
   ......
   99) Exit the Social-Engineer Toolkit
```

首先，选择菜单中第一个选项，社会工程学攻击。

```
1) Spear-Phishing Attack Vectors
2) Website Attack Vectors  // 选择2，网站攻击
3) Infectious Media Generator
4) Create a Payload and Listener
5) Mass Mailer Attack
6) Arduino-Based Attack Vector
7) Wireless Access Point Attack Vector
8) QRCode Generator Attack Vector
9) Powershell Attack Vectors
10) SMS Spoofing Attack Vector
11) Third Party Modules
```

然后，选择菜单中第二个选项，网站攻击。

```
1) Java Applet Attack Method
2) Metasploit Browser Exploit Method
3) Credential Harvester Attack Method  // 选择3，窃取凭证
4) Tabnabbing Attack Method
5) Web Jacking Attack Method
6) Multi-Attack Web Method
7) Full Screen Attack Method
8) HTA Attack Method
```

选择第三个选项，窃取凭证。

```
1) Web Templates  // 使用预定义的网站模板
2) Site Cloner    // 克隆网页
3) Custom Import  // 从指定目录导入网站
```

在此，为了方便，我们直接选择 1，使用 SET 中内置的网站模板来进行实验。

```
set:webattack> IP address for the POST back in Harvester/Tabnabbing [192.168.1.107]:
```

此处注意了，它这里会使用你的默认 ip，也就是你的第一个 ip：

![][24]

如果你使用的是双网卡，你想渗透其他内网网段的主机，可以先回车，回车后看到了提示：

![][25]

新建一个终端，编辑下`/etc/setoolkit/set.config`这个文件，把网卡改一下就 OK 了：

![][26]

选择 2，使用 Google 登录页面作为钓鱼网站：

![][27]

当出现

```
[*] Harvester is ready, have victim browse to your site.
```

这一行的时候表示就可以开始钓鱼了，此时在受害者的电脑上打开我们攻击机的 ip 就是我们的钓鱼 google 界面：

![][28]

同时，SET 的控制台打印出来一条访问请求记录：

![][29]

但是，我们这个也太明显了吧，谁不知道 192.168.\*是内网 ip，所以我们配合 Ettercap 一起使用：

将以下内容添加到`/etc/ettercap/etter.dns`中

```
google.com       A      192.168.1.107
*.google.com     A      192.168.1.107
www.google.com   PTR    192.168.1.107
```

![][30]

然后执行 ettercap：

```
ettercap -TqM ARP -P dns_spoof /192.168.1.106///
```

具体的参数前面都解释过了，然后用受害者机器访问`google.com`：

![][31]

可以看到打开的是我们的钓鱼界面，然后我们登陆一下：

![][32]

可以看到我们的 Ettercap 和 SET 都得到了账户名和密码！钓鱼成功

但是存在以下不足：

1.未考虑 HTTPS 的情况，HTTPS 的访问不会转发到目标 IP。

2.钓鱼网页的点击登录后，应该跳转到正常的网站首页，而不是仍停留在登录页面。

### BetterCap

中间人攻击最知名的莫过于 ettercap，而开发 bettercap 的目的不是为了追赶它，而是替代它，原因如下：

- ettercap 很成功，但在新时代下它已经老了
- ettercap 的过滤器复杂，使用门槛高
- 在大型网络下，主机发现功能效果很差
- 优化不够，对研究人员来说，无用的功能太多
- 扩展性不够，开发需要掌握 C/C++语言

> Bettercap 的更新频率还是比较高的，新版的 bettercap 采用类 msf 的嵌入式终端界面，这种终端界面给人一种沉浸式的体验，但是也存在一些问题，比如输入和输出混在一起的问题以及行标刷新的问题
> 这版 bettercap 的功能可以说是极大的丰富了，从原来的一个单纯的网络分析器真正的向所有的“cap”过渡了，不但支持以前的内网 arp 和 dns 欺骗，还提供了低功耗蓝牙(BLE)、GPS 的嗅探以及给网络内指定 MAC 的设备发送远程唤醒信号(Wake On LAN)等功能，可以说已经非常强大了

下载地址(有 win 版)：https://github.com/bettercap/bettercap/releases/latest

Kali 没有自带：`apt-get install bettercap -y`

先看一下有哪些基本参数：`bettercap -h`

![][33]

参数解释：

|           参数           |                                 含义                                 |
| :----------------------: | :------------------------------------------------------------------: |
|    -autostart string     |                    使用逗号分割自动启动需要的模块                    |
|      -caplet string      |                 从文件中读取命令并在交互式会话中执行                 |
|    -cpu-profile file     |                          写 cpu 配置文件。                           |
|          -debug          |                            打印调试消息。                            |
|     -env-file string     |                           加载环境变量文件                           |
|       -eval string       | 运行一个或多个以;分隔的命令;在交互式会话中，用于通过命令行设置变量。 |
| -gateway-override string | 使用提供的 IP 地址而不是默认网关。如果未指定或无效，将使用默认网关。 |
|      -iface string       |           要绑定的网络接口，如果为空，将自动选择默认接口。           |
|    -mem-profile file     |                       将内存配置文件写入文件。                       |
|        -no-colors        |                          禁用输出颜色效果。                          |
|       -no-history        |                       禁用交互式会话历史文件。                       |
|         -silent          |                        禁止所有非错误的日志。                        |

那么我们用`bettercap`打开看一下：

![][34]

打开之后则会自动开始探测当前网段内主机，输入 help ,可以看到许多设置选项：

![][35]

以下为参数解释：

|:-----:|:-----:|
|help MODULE|如果未提供模块名称，则列出可用命令或显示模块特定帮助。|
|active|显示有关活动模块的信息。|
|quit|关闭会话并退出。|
|sleep SECONDS|睡眠给定的秒数。|
|get NAME|获取变量 NAME 的值，单独使用*，或使用 NAME *作为通配符。|
|set NAME VALUE|设置变量 NAME 的 VALUE。|
|read VARIABLE PROMPT|显示 PROMPT 以询问用户输入将保存在 VARIABLE 中的输入。|
|clear|清除屏幕。|
|include CAPLET|在当前会话中加载并运行此 caplet。|
|! COMMAND|执行 shell 命令并打印其输出。|
|alias MAC NAME|给定其 MAC 地址为给定端点分配别名。|

模块说明：

|:-----:|:-----:|
|any.proxy|防火墙重定向到任意指定代理|
|api.rest|RESTful API 模块|
|arp.spoof|arp 欺骗模块|
|ble.recon|低功耗蓝牙设备发现模块|
|caplets|用于列出和更新 caplets 模块|
|dhcp6.spoof|dhcp6 欺骗模块(通过伪造 DHCP 数据包篡改客户端的 DNS 服务器，因此需要与 dns.spoof 一并启用)|
|dns.spoof|回应 dns 欺骗报文|
|events.stream|默认启用此模块，负责在交互式会话期间显示时间流|
|gps||
|http.proxy|HTTP 透明代理，可以使用 Javascript 模块|
|http.server|HTTP 服务器|
|https.proxy|HTTPS 透明代理|
|https.server|HTTPS 服务器|
|mac.changer|修改活跃接口的 mac 地址|
|mysql.server||
|net.probe|通过向子网内每个可能存在的 IP 发送 UDP 数据探测网络中主机|
|net.recon||
|net.sniff|网络嗅探模块|
|packet.proxy||
|syn.scan|执行 syn 的端口扫描 |
|tcp.proxy||
|ticker||
|update||
|wifi|wifi 模块，有 deauth 攻击（wifi 杀手）和创建软 ap 的功能|
|wol||

每个模块的详细使用方法可参考这篇文章：https://blog.csdn.net/u012570105/article/details/80561778

Bettercap 实战

在 Bettercap 中设置需要欺骗的网址和自己的恶意服务器 IP：

```
set dns.spoof.domains *.baidu.com
set dns.spoof.address 1.1.1.1
dns.spoof on
```

![][36]

Windows7 中设置 DNS 服务器地址为自己的 IP 地址：

![][37]

刷新 DNS 后通过 ping 命令(此处 ping 不通我存有疑惑，ipv4 转发是开启的)：

![][38]

在我们的 Kali 端就能看到 DNS 请求信息：

![][39]

### Cain & Abel

> Cain & Abel 是由 Oxid.it 开发的一个针对 Microsoft 操作系统的免费口令恢复工具。号称穷人使用的 L0phtcrack。它的功能十分强大，可以网络嗅探，网络欺骗，破解加密口令、解码被打乱的口令、显示口令框、显示缓存口令和分析路由协议，甚至还可以监听内网中他人使用 VOIP 拨打电话。

下载地址：http://www.oxid.it/cain.html，需要[winpacp][40]的支持，但是winpacp的下载界面上写着这么一句话：The WinPcap project has ceased development and WinPcap and WinDump are no longer maintained. We recommend using Npcap instead：WinPcap 项目已经停止开发，WinPcap 和 WinDump 也不再维护。我们建议使用 Npcap 代替。

所以我们直接去下载 npacp：https://nmap.org/npcap/，最新版的是0.99-r9版本，[点我下载][41]

安装的时候除了默认选项，多勾选最下面那个选项：Install Npcap in WinPacp API-compatible Mode 即可满足 Cain & Abel 对 winpacp 的支持要求

Cain & Abel 主界面长这样：

![][42]

看一下 Tool 界面，看出来主要功能还是密码破解：

![][43]

# ARP 欺骗

## 原理

arp

> 地址解析协议，即 ARP（Address Resolution Protocol），是根据 IP 地址获取物理地址的一个 TCP/IP 协议。主机发送信息时将包含目标 IP 地址的 ARP 请求广播到网络上的所有主机，并接收返回消息，以此确定目标的物理地址；收到返回消息后将该 IP 地址和物理地址存入本机 ARP 缓存中并保留一定时间，下次请求时直接查询 ARP 缓存以节约资源。

arp 欺骗

> ARP 欺骗（英语：ARP spoofing），又称 ARP 毒化（ARP poisoning，网上上多译为 ARP 病毒）或 ARP 攻击，是针对以太网地址解析协议（ARP）的一种攻击技术，通过欺骗局域网内访问者 PC 的网关 MAC 地址，使访问者 PC 错以为攻击者更改后的 MAC 地址是网关的 MAC，导致网络不通。此种攻击可让攻击者获取局域网上的数据包甚至可篡改数据包，且可让网上上特定计算机或所有计算机无法正常连线。

## 实现

在 Linux 下实现 arp 欺骗最经典的工具：`arpspoof`(比较稳定)，也可使用 ettercap 和 bettercap

在 Windows 下可使用

查看本机 arp 缓存表：

(通用)`arp -a`：不过在 Linux 下执行较慢

(Linux)`ip neigh show`：实现上是通过另一种系统调用 netlink 来获取的

如果 arp 欺骗一直不成功，可使用`arp -d`删除 arp 缓存表(需管理员权限)

### arpspoof

arpspoof 即可进行单向欺骗，也可进行双向欺骗(开两个终端)，一般参数如下：

```
arpspoof -i [网卡] -t [被欺骗主机] [自己想要伪装的主机]

-i指定的是网卡，-t指定的是目标(target)，如果不指定则对整个网段进行arp毒化
```

所以我们这里想要欺骗 win7(192.168.1.106)我是网关(192.168.1.1)，并想要欺骗网关我是 win7，可以使用以下命令

```
arpspoof -i eth0 -t 192.168.1.106 192.168.1.1
arpspoof -i eth0 -t 192.168.1.1 192.168.1.106
```

我们先来看一下没有进行 arp 欺骗之前 win7 的 arp 缓存表：

![][44]

然后开启欺骗：

![][45]

再次查看 arp 缓存表：

![][46]

发现原来网关的 mac 地址变得和 kali 的一样了，那么我们向网关发送的所有流量都会流经 kali，而 kali 也同时欺骗着网关自己是 win7，这样 win7 能正常上网但它不知道所有流量都被窥视了。

但在这里建议把 Linux 内核的流量转发功能开启，不然可能导致对方上不了网，引起对方的警觉：

```
sysctl net.ipv4.ip_forward
sysctl -w net.ipv4.ip_forward=1
```

![][47]

### ettercap

前面已经介绍过详细使用方法，此处直接给出命令：

```
ettercap -i eth0 -TqM ARP /192.168.1.106// ///
```

![][48]

和上面起到的是一样的效果

### bettercap

同样我们使用`bettercap`命令进入，执行以下命令：

```
net.sniff on
set arp.spoof.targets 192.168.1.106
(设定只针对一个或多个目标，不设置则针对整个网段开始欺骗)
arp.spoof on
```

此时就开始了 arp 欺骗，如果此时我们用 wireshark 等抓包工具去抓的话，会发现只抓得到 tcp 数据包，没有 http/https 的数据包，可以通过命令`http.proxy on`或者`https.proxy on`开启 http/https 代理

如果想开个窗口监视 http 的网页浏览，可以使用 `urlsnarf -i eth0` 命令(urlsnarf 命令需用在 arp 欺骗之后)：

![][49]

Driftnet 可用于过滤嗅探图片，利用 driftnet 进行流量监控，显示被害者浏览的图片：`driftnet -i eth0`：

![][50]

而 driftnet 和 arpspoof 都属于 Dsniff 工具套件

[1]: https://www.freebuf.com/column/179597.html
[2]: https://www.freebuf.com/articles/network/183692.html
[3]: https://www.freebuf.com/company-information/194558.html
[4]: https://blog.csdn.net/zpy1998zpy/article/details/81038016
[5]: https://www.freebuf.com/column/174713.html
[6]: https://www.freebuf.com/articles/web/190947.html
[7]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_105813.png
[8]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_131910.png
[9]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_110038.png
[10]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_132223.png
[11]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_132555.png
[12]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_110341.png
[13]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_110529.png
[14]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_133129.png
[15]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_133247.png
[16]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_133405.png
[17]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_134745.png
[18]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_110721.png
[19]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_111143.png
[20]: https://github.com/thelinuxchoice/blackeye
[21]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_142229.png
[22]: https://www.freebuf.com/sectool/99607.html
[23]: https://www.freebuf.com/articles/network/183692.html
[24]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_111546.png
[25]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_111737.png
[26]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_144520.png
[27]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_145243.png
[28]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_112144.png
[29]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_112221.png
[30]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_112611.png
[31]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_114106.png
[32]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_114354.png
[33]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190215_172938.png
[34]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_114826.png
[35]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_115036.png
[36]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_120727.png
[37]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_121150.png
[38]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_095058.png
[39]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_121350.png
[40]: https://www.winpcap.org/install/
[41]: https://nmap.org/npcap/dist/npcap-0.99-r9.exe
[42]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190217_173819.png
[43]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190217_174017.png
[44]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_121540.png
[45]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_121848.png
[46]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_121930.png
[47]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_103057.png
[48]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_125447.png
[49]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_140746.png
[50]: https://img.soapffz.com/archives_img/2019/02/15/archives_20190216_140552.png
