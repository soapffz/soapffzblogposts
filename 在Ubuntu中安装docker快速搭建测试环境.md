---
title: "在Ubuntu中安装docker快速搭建测试环境"
categories: ["安全技术"]
tags: ["渗透环境搭建", "Ubuntu", "Docker"]
draft: false
slug: "18"
date: "2019-01-29 21:45:00"
---

# 为啥要用 docker?

在实际学习中，经常需要模拟不同的漏洞环境，而使用公网的实例的话，多多少少又存在一些风险，因此能搭建一个本地的模拟环境去测试漏洞是一个不错的方案。Docker 是近两年来十分流行的开源容器引擎，因此也出现了很多使用 Docker 容器搭建的靶机环境供新手学习和使用。

写这篇文章的原因：我一直知道 Docker 的强大，但是需要一个例子来开始

这两篇公众号文章：

- https://mp.weixin.qq.com/s/BShKqciii4hoRM3MMyVCbA
- https://mp.weixin.qq.com/s/7VMd0YAQD4nNxY0auzdJBA

是我下定决心安装 Docker 的动力

# 为什么是在 Ubuntu 中？

我们常见的测试环境有 Win10、Kali、Win7、Win2008、Win2003 等，再来一个 Linux 环境最合适的就是 Ubuntu 了

我们大部分人常用的环境是 Win10(说 MacOS 的坐下！)，那在 Win10 安装 Docker 怎么样呢？

Docker for Widows 官方文档：https://docs.docker.com/docker-for-windows/install/ 里面说了

Win10 家庭版是不支持 Docker for Windows 的，Win10 其他版本，常见的比如专业版(我自己也装的这个)需要在 BIOS 中开启 Virtualization 虚拟化功能，我自己试过很多次不能用 Docker for windows，开启 Hyper-V 的话连接校园网的软件会报错“不能在虚拟环境中运行软件”

那不支持安装环境的机器只能使用 Docker Toolbox，文档地址：https://docs.docker.com/toolbox/toolbox_install_windows/

Docker Toolbox 是需要配合 virtualbox 使用的，然后我为什么用 Ubuntu 去安装 docker 呢？

- 需要一个轻量级桌面 Linux 靶机
- 虚拟机可以经常恢复快照(虽然 docker 的存在能大幅消减快照的繁琐)
- 就想用！(傲娇脸)

# 安装 docker

## 安装

**我这里由于比较懒，直接 su root 切换到了 root 账户下进行，所以如果命令执行异常的，加上 sudo 在前面**

- 安装所需要的包(这里默认你的 ubuntu 已经配置过国内 apt 镜像)：apt install docker.io
- 安装完成查看版本信息：docker -v
- 添加权限（可选）：将当前用户添加到 docker 用户组，可以不用 sudo 运行 docker（需要重新登录）：sudo usermod -aG docker \$USER

## 配置镜像加速

和 Git 一样，默认的镜像由于服务器都在国外，速度很慢，所以需要换国内镜像

最新版本的 docker 的配置文件是/etc/docker/daemon.json，默认安装完 docker 时是不存在的，使用 vim 打开则自动创建

vim /etc/docker/daemon.json，将以下代码粘贴进去：

```
{
  "registry-mirrors": ["http://example.m.daocloud.io"]
}
```

这个镜像地址有如下推荐：

- 网易加速器：http://hub-mirror.c.163.com
- 官方中国加速器：https://registry.docker-cn.com
- ustc 的镜像：https://docker.mirrors.ustc.edu.cn
- 可以去阿里云上配置一个自己的镜像加速器：
- 先登录阿里开发者平台：https://dev.aliyun.com/search.html
- 登录后，进入 Docker 镜像仓库：https://cr.console.aliyun.com/cn-hangzhou/mirrors，选中加速器 Tab，这里可以看到，系统已经为我们生成了一个专属加速器地址：https://xxxxx.mirror.aliyuncs.com
- 也可以在 DaoCloud 上配置一个：
- 在 Daocloud 主业：https://www.daocloud.io/ 注册并登陆
- 在主页右上角有一个火箭按钮：

![][1]

- 之后会弹到一个广告界面：https://www.daocloud.io/mirror，看起来是广告，实际已经为我们生成了一个唯一的加速器地址，往下拉一下找到配置教程处：

![][2]

打了马赛克的位置就是加速器地址

**速度推荐**：自己拉取了一个 wordpress 感觉一下，阿里云和 DaoCloud 的速度差不多，其他的稍差，个人推荐使用 DaoCloud

然后重启 docker 服务：service docker restart 就可以了，我们可以拉一个 wordpress 测试一下：docker pull wordpress

#### 搭建 wordpress 示例测试环境

**可以**使用官方出品的 Docker 镜像：`docker pull wpscanteam/vulnerablewordpress`

![][3]

pull 完毕后运行，转发 80 和 3306 端口。

```
docker run --name vulnerablewordpress -d -p 80:80 -p 3306:3306 wpscanteam/vulnerablewordpress
```

![][4]

打开 ip 即可进入 wordpress 安装界面：

![][5]

**也可以**自己用 wordpress 和 mysql5.6 搭建顺便学习下指令，教程如下：

1.配置好镜像地址后，我们拉取 wordpress 镜像 `docker pull wordpress` 和 mysql5.6 镜像 `docker pull mysql:5.6`

拉取示意图：

![][6]

2.创建 mysql 容器

```
docker run --name testmysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=a123456 -d mysql:5.6
#参数解释:
#MYSQL_ROOT_PASSWORD=a123456 设置mysql的root密码是a123456
#testmysql 设置容器名称为testmysql 这个名字以后会用到要记住，生成后会返回一个id
```

![][7]

3.登录到 mysql 创建数据库

```
docker exec -it testmysql mysql -uroot -p
#此处的 testmysql 是之前mysql容器的名字
```

输入之前设置的 root 密码(a123456)登录到数据库:

![][8]

4.创建数据库

`create database wordpress;`

按 ctrl+D 或者输入 quit;退出

![][9]

5.创建 wordpress 容器,和创建 mysql 容器类似

```
docker run --name testwordpress --link testmysql:db -p 80:80 -d wordpress:latest
#参数解释:
#80:80 将容器的80端口和主机的80端口互通
#testmysql:db 将wordpress容器连接上mysql容器并起别名为db
```

![][10]

6.在浏览器打开主机的 ip,就能跳转到 wordpress 的安装界面了：

![][11]

- 用户名:root (mysql 的 root 用户)
- 密码:a123456 (还记得设置的 mysql 的 root 密码吗?)
- 数据库主机:db(还记得刚刚设置的别名吗?)

![][12]

其他默认,就安装完成了：

![][13]

一个渗透测试环境就搭建完成了

比较文章开头提到的文章中下载 wordpress 镜像，用 virtualbox 搭建是不是方便许多？

## 常用 docker 命令

- docker version：查看版本号
- docker run hello-world：载入测试镜像测试
- docker images：查看当前有哪些镜像
- docker ps：查看所有正在运行容器
- docker ps -a：查看所有容器
- docker stop containerId(容器的 ID)：关闭 ID 为 xxx 的容器
- docker rm containerId(容器的 ID)：删除 ID 为 xxx 的容器
- 镜像删除：
- 停止所有的 container，这样才能够删除其中的 images：docker stop \$(docker ps -a -q)
- 如果想要删除所有 container 的话再加一个指令：docker rm \$(docker ps -a -q)
- 删除 images，通过 image 的 id 来指定删除谁：docker rmi <image id>
- 想要删除 untagged images，也就是那些 id 为<None>的 image 的话可以用：docker rmi $(docker images | grep "^<none>" | awk "{print $3}")
- 要删除全部 image 的话：docker rmi \$(docker images -q)
- 设置容器的端口映射：docker run [-P][-p]
- -P: 对容器所有的端口进行映射
- -p: 指定映射哪些容器的端口
- 几个例子：
- containerPort 只指定容器的端口，宿主机的端口随机映射：docker run -p 80 -i -t /bin/bash
- hostPort:ContainerPort 同时制定宿主机端口以及容器端口：docker run -p 8080:80 -i -t /bin/bash0
- ip:containerPort 指定 ip 和容器的端口：docker run -p 0.0.0.0:80 -i -t /bin/bash
- ip:hostPort:ContainerPort 同时制定 ip 以及宿主机端口以及容器端口：docker run -p 0.0.0.0:8080:80 -i -t /bin/bash

[1]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_220730.png
[2]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_220813.png
[3]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_114643.png
[4]: https://img.soapffz.com/archives_img/2019/01/30/archives_20190130_114840.png
[5]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_225159.png
[6]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_222141.png
[7]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_224746.png
[8]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_224848.png
[9]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_224959.png
[10]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_225051.png
[11]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_225159.png
[12]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_225519.png
[13]: https://img.soapffz.com/archives_img/2019/01/29/archives_20190129_225557.png
