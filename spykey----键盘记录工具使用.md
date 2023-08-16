---
title: "spykey -- 键盘记录工具使用"
categories: [ "安全技术" ]
tags: [ "Kali","渗透工具" ]
draft: false
slug: "46"
date: "2019-03-18 21:12:00"
---

# 起因

键盘记录这个，嗯，肯定要说一下

# 环境及准备

## 环境

- Kali 2019.1
- Win7 SP1

## 源码下载

- 作者 GitHub：https://github.com/thelinuxchoice/spykey

- 我拷贝过来了：https://gitee.com/soapffz/spykey

就一个`spykey.sh`和两个 ico 应用图标(伪装用)

** 需要 mingw-w64 的支持**：

```
sudo apt-get install mingw-w64 -y
```

# 使用

进入 spykey 文件夹赋予`spykey.sh`可执行权限然后执行即可：

```
chmod 755 spykey.sh
./spykey.sh
```

![][1]

然后依次会有几个选项，分别是：

- 选择端口 默认就好
- Payload name 生成的记录器的名字，这个其实下载下来之后重命名就 ok，这里随便输
- 日志的名字 用于查看记录到了写什么
- 选择图标 这里只提供了两个国外著名社交软件`messenger`和`whatsapp`的 ico，可以自定义添加

![][2]

作者还提醒不要上传到[virustotal][3]哈哈，然后就会生成 payload，是用作者提供的服务器下载的

你可以直接诱导受害者通过这个链接下载，也可以下载下来做些文章再发给对方(比如把这个捆绑在正常的 exe 里咳咳我什么都没说)

可以看到，这里作者备用的下载地址挂掉了，生成 payload 之后，kali 就开始监听了

我们发给我们在同一网段(和 Kali 同 NAT 网络)下的 Win7，在 Win7 双击 Payload.exe 就连接上了，打一段字看下效果：

![][4]

在 Kali 输入`type log的名字`查看：

![][5]

发现了小毛病，比如 ctrl 和 shift、win 这些快捷键都没记录，不过无伤大雅，因为我们要记录的东西自己心里都清楚

那么同网段的虚拟机可以了，那我们试下其他环境

- 室友的电脑+同某运营商学生端

寝室的网络是通过某罪恶的运营商分配的 PPP 适配器，说白了还是内网

网段从`172.31.0.1`到`172.31.xxx(不知道).255`，室友此时的 ip：

![][6]

重新弄一个 payload 放在 U 盘里插室友：(好像少了几个字？)

![][7]

好的，还是 127.0.0.1

- 室友的电脑+我开热点

用我的手机开热点，重新弄一个 payload 放在 U 盘里插室友：

![][8]

Ok，还是 127.0.0.1，实验到此结束

得出：不是我们本地自己的连接，是都在工具作者的服务器上连接的，emmm，这样不太好，那岂不是我们看得到什么，作者就看得到什么

# 总结

| 优点                                     | 缺点                       |
| ---------------------------------------- | -------------------------- |
| 简单，设置名字下载传给对方就能用         | 服务器是大佬的，信息易泄露 |
| 只要能上网，就能被监听                   | 得一直监听                 |
| 免杀性高，不做免杀处理都能对抗大部分杀软 | 功能性还有待提高           |
| 服务不用自己搭                           | 端口变更，每次都得重新生成 |

结尾：

整个过程中：

**火绒一点反应都没有。。**

**火绒一点反应都没有。。**

**火绒一点反应都没有。。**

[1]: https://img.soapffz.com/archives_img/2019/03/18/archives_20190318_211718.png
[2]: https://img.soapffz.com/archives_img/2019/03/18/archives_20190318_213532.png
[3]: https://www.virustotal.com/#%2525252525252525252525252Fhome%2525252525252525252525252Fupload=true
[4]: https://img.soapffz.com/archives_img/2019/03/18/archives_20190318_214108.png
[5]: https://img.soapffz.com/archives_img/2019/03/18/archives_20190318_214149.png
[6]: https://img.soapffz.com/archives_img/2019/03/18/archives_20190318_215852.png
[7]: https://img.soapffz.com/archives_img/2019/03/18/archives_20190318_215132.png
[8]: https://img.soapffz.com/archives_img/2019/03/18/archives_20190318_220449.png