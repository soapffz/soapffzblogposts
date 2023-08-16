---
title: "docker搭建pikachu及burp暴力破解基于Token的表单"
categories: [ "安全技术" ]
tags: [ "Docker","爆破","靶机","burpsuite" ]
draft: false
slug: "462"
date: "2020-01-30 17:24:00"
---

## 事情起因

持续整理笔记中

参考文章：

- [burp 暴力破解基于 Token 的表单][1]

## 安装 docker

```
apt-get install docker.io -y
```

然后使用`docker -v`命令验证是否安装完成：

![][2]

### 换镜像

- 网易加速器：http://hub-mirror.c.163.com
- 官方中国加速器：https://registry.docker-cn.com
- ustc 的镜像：https://docker.mirrors.ustc.edu.cn

可以去阿里云上配置一个自己的镜像加速器：

先登录[阿里开发者平台][3]，登录后，进入`Docker`[镜像仓库][4]

选中加速器`Tab`，这里可以看到，系统已经为我们生成了一个专属加速器地址：

https://xxxxx.mirror.aliyuncs.com

```
vim /etc/docker/daemon.json
```

基本配置如下：

```
{
    "registry-mirrors": ["https://xxxxx.mirror.aliyuncs.com"],
    "graph": "/mnt/docker-data",
    "storage-driver": "overlay"
}
```

后面两条是我在使用的过程中遇到的问题，好像是软件驱动的问题

反正加上就对了，然后重启 docker 服务：

```
systemctl daemon-reload
service docker restart
```

就可以了

## 安装 pikachu

`pikachu`靶场没有现成的镜像源，需要我们自己`build`

```
git clone https://github.com/zhuifengshaonianhanlu/pikachu
cd pikachu
docker build -t "pikachu" .
```

使用当前目录 kerfile 创建镜像，命为`pikachu`。要和 Dockerfile 在同一目录，注意命令后面还有一个点

中间会拉取`lnmp`环境，大约有`200M`

```
docker run -it -d -p 8082:80 pikachu
```

- -i: 以交互模式运行容器，通常与 -t 同时使用
- -t: 为容器重新分配一个伪输入终端，通常与 -i 同时使用
- -d: 后台运行容器，并返回容器 ID
- -- name：为容器起一个名称
- -v /xxx:/yyy：把宿主机的 xxx 目录挂载到容器的 yyy 目录
- -p: 指定要映射的 IP 和端口，但是在一个指定端口上只可以绑定一个容器
- 设置容器的端口映射：docker run [-P][-p]
- containerPort 只指定容器的端口，宿主机的端口随机映射：docker run -p 80 -i -t /bin/bash
- hostPort:ContainerPort 同时制定宿主机端口以及容器端口：docker run -p 8080:80 -i -t /bin/bash0
- ip:containerPort 指定 ip 和容器的端口：docker run -p 0.0.0.0:80 -i -t /bin/bash
- ip:hostPort:ContainerPort 同时制定 ip 以及宿主机端口以及容器端口：docker run -p 0.0.0.0:8080:80 -i -t /bin/bash

![][5]

首页有一个初始化按钮，点击初始化后即可

![][6]

![][7]

## burp 设置

可以按照老方法，浏览器设置里面搜索代理，设置自定义本地及局域网代理为`127.0.0.1:8080`

也可以直接使用浏览器插件[`SwitchySharp`][8]

安装后在选项中自定义一个`burpsuite`的模式

![][9]

然后就可以在右上角插件图标快捷切换模式

![][10]

平时就使用系统代理设置，需要`burp`拦截时就可以一键切换

另外如果你的靶场的`ip`是本地的，`burp`默认拦截`127.0.0.1:8080`就可以

如果像我一样靶机没有在本机，那么需要把`burp`设置为拦截所有 ip

在`proxy`选项卡的`settings`中选中默认的`127.0.0.1:8080`，

点击左边的`Edit`，修改为第二个选项`All interfaces`

![][11]

这样也能拦截不是本机`ip`的`response`

## pikachu 靶场 token 表单爆破

设置好代理后，选中靶场的暴力破解的`token防爆破？`靶场

开启拦截，随便填写数据，`burp`拦截到数据包

![][12]

`F12`看一下源码发现`token`值写在`login`表单下面一点

![][13]

右键将请求包转送到 Intruder

猜测`token`值只与密码有关，于是我们`clear`清除干净之后

只选择`password`和`token`值，并且上面攻击模式`Attack type`设置为`Pitchfork`

![][14]

在`options`栏找到`Grep - Extract`，点击`Add`

点击`Refetch response`，进行一个请求，即可看到响应报文，直接选取需要提取的字符串

上面的会自动填入数据的起始和结束标识。

![][15]

切换`payloads`选项卡，第一个`payload`设置为`Simple list`即字典模式

![][16]

在下方添加字典，第二个`payload`设置为`Recursive grep`

![][17]

`payload`中有`Recursive grep`选项时不支持多线程，在`options`把线程改为 1

线程为 1 完全没问题，`burp`发包速度很快的，点击右上角`Attack`开始攻击

![][18]

爆破成功！

本文完。

[1]: https://mp.weixin.qq.com/s/JnMXYG609ukaM-remtE_-w
[2]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_174617.png
[3]: https://dev.aliyun.com/search.html
[4]: https://cr.console.aliyun.com/cn-hangzhou/mirrors
[5]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_152907.png
[6]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_152820.png
[7]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_152834.png
[8]: https://chrome.google.com/webstore/detail/proxy-switchysharp/dpplabbmogkhghncfbfdeeokoefdjegm?h1=zh
[9]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_180348.png
[10]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_170051.png
[11]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_165911.png
[12]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_170119.png
[13]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_170155.png
[14]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_172058.png
[15]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_170855.png
[16]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_171336.png
[17]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_171353.png
[18]: https://img.soapffz.com/archives_img/2020/01/30/archives_20200130_172148.png