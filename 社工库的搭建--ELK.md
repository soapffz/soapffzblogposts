---
title: "社工库的搭建--ELK"
categories: ["安全技术", "工具分享"]
tags: ["信息收集", "社工库", "ELK"]
draft: false
slug: "364"
date: "2019-07-29 16:27:00"
---

** 声明：作者初衷用于分享与普及网络安全知识，若读者因此作出任何危害网络安全行为后果自负，与作者及本网站无关 **

** 本人及本站自始至终未向任何人提供任何网站、企业和组织的任何信息和资料 **

# 起因

出于学习的目的，每一个像我这样的网络安全爱好者都会多多少少有一些网上流出的“裤子”

那么随着数据量的增多以及合法渗透测试中的信息收集需求，搭建一个本地的、查询迅速准确的社工库是很有必要的

那么搭建需要哪些环境呢？

> 目前网上已经搭建好的社工库，大部分是 mysql+coreseek+php 架构，coreseek 基于 sphinx，是一款优秀的全文搜索引擎，但缺点是比较轻量级，一旦数据量过数亿，就会有些力不从心，并且搭建集群做分布式性能并不理想，如果要考虑以后数据量越来越大的情况，还是得用其他方案

我这里使用一个叫做`ELK`的方式，原本是一个开源实时日志分析平台

本篇文章将介绍`ELK`环境的搭建以及常用的数据导入及查询方式

# ELK 介绍

ELK 是什么东西？

> ELK 是三个开源软件的缩写，分别为：Elasticsearch 、 Logstash 以及 Kibana , 它们都是开源软件。不过现在还新增了一个 Beats，它是一个轻量级的日志收集处理工具(Agent)，Beats 占用资源少，适合于在各个服务器上搜集日志后传输给 Logstash，官方也推荐此工具，目前由于原本的 ELK Stack 成员中加入了 Beats 工具所以已改名为 Elastic Stack。Elastic Stack 包含：

> Elasticsearch 是个开源分布式搜索引擎，提供搜集、分析、存储数据三大功能。它的特点有：分布式，零配置，自动发现，索引自动分片，索引副本机制，restful 风格接口，多数据源，自动搜索负载等。详细可参考 Elasticsearch 权威指南

> Logstash 主要是用来日志的搜集、分析、过滤日志的工具，支持大量的数据获取方式。一般工作方式为 c/s 架构，client 端安装在需要收集日志的主机上，server 端负责将收到的各节点日志进行过滤、修改等操作在一并发往 elasticsearch 上去。

> Kibana 也是一个开源和免费的工具，Kibana 可以为 Logstash 和 ElasticSearch 提供的日志分析友好的 Web 界面，可以帮助汇总、分析和搜索重要数据日志。

> Beats 在这里是一个轻量级日志采集器，其实 Beats 家族有 6 个成员，早期的 ELK 架构中使用 Logstash 收集、解析日志，但是 Logstash 对内存、cpu、io 等资源消耗比较高。相比 Logstash，Beats 所占系统的 CPU 和内存几乎可以忽略不计

ELK Stack （5.0 版本之后）--> Elastic Stack == （ELK Stack + Beats）。目前 Beats 包含六种工具：

为什么用 ELK?

> 传统的社工库通常用 MySQL 数据库来进行搭建，在相当大的数据下检索效率非常低下。在这种关系型数据库中进行查询需要明确指定列名。而在 ES 中可用全文 检索，并且在大数据的查询中的响应几乎都是毫秒级的，速度相当之快！ELK 原本用在日志的大数据收集和分析，其可怕的速度作为社工库也是一种不错的选择。

[ELK 官网][1]，[ELK 三款软件下载][2]，[ELK 中文指南(需登录)][3]

# ELK 环境搭建

## java 环境配置

`ELK`需要`java`环境的支持，并且配置`JAVA_HOME`环境变量

由于`java`各个版本的收费与不收费的混乱，我一直保持使用`java8`的版本，

祭出我一直使用的`jdk`环境：[点我去下载][4]，像`burpsuite`1.7 也能直接在这个环境下使用

但是使用`Elasticsearch`已经提示即将不支持`java`8，请尽快升级到`java`11，这里顺便介绍下`jre`和`jdk`：

前者为`Java Runtime Environment`，即`java`运行环境，是运行`java`文件的最小环境，

后者为`Java SE Development Kit`，即`java`开发环境工具包，是对`java`编程的环境，

对于小白来说，建议直接安装`jdk`，`jdk`是包含`jre`的，下载完记得手动添加安装位置到环境变量：

`java`默认安装路径：`C:\Program Files\Java`，里面同时有`jre`和`jdk`，

而且`jdk`文件夹里面还有一个`jre`文件夹，新建一个系统变量`JAVA_HOME`，值为`jdk`路径

然后`PATH`新建添加`%JAVA_HOME%\bin;%JAVA_HOME%\jre\bin`，就配置好`JAVA_HOME`这个环境变量了

![][5]

## 基础运行

下载好`Elasticsearch`、`Logstash`以及`Kibana`三个压缩包后都解压，

1.在`Elasticsearch`文件夹的`bin\`目录下打开`cmd`，输入`elasticsearch.bat`:

![][6]

浏览器里打开：`http://localhost:9200/`：

![][7]

2.在`kibana`文件夹里打开`config\kibana.yml`，将末尾的

```
#i18n.locale: "en"
```

改为：

```
i18n.locale: "zh-CN"
```

保存后在`kibana`文件夹里点击`bin\kibana.bat`文件

![][8]

浏览器打开：`http://localhost:5601`，首次打开界面如图所示：

![][9]

到到这里基本就运行起来了。这里还需要介绍几个主要的配置文件文件及作用：

主节点配置文件`elasticsearch.yml`，为什么叫做主节点，因为`ELK`本来就是为了分布式的架构的日志分析而设计的

位置在`elasticsearch\config\elasticsearch.yml`，一般不建议修改，默认的就可以。

```
#禁用虚拟内存，提高性能
bootstrap.memory_lock: true
#节点名称自定义：
cluster.name: elasticsearch
#数据通信端口：
http.port: 9200
#监听网卡ip
network.host: 192.168.1.1
#是否是数据节点：
node.data: true
#关闭即可：
node.ingest: true
#是否是主节点,不定义的话先启动的是主节点：
node.master: true
#最大存储节点：
node.max_local_storage_nodes: 1
#节点名字自定义：
node.name: Win-Master-1
#数据文件路径
path.data: D:\elk\elasticsearch\data
path.logs: D:\elk\elasticsearch\logs
#节点间通信端口：
transport.tcp.port: 9300
#节点ip，节点之间要允许ping和9300端口通信
discovery.zen.ping.unicast.hosts: ["192.168.1.1", "192.168.1.2"]
#head插件相关：
http.cors.enabled: true
http.cors.allow-origin: "*"
# 0.0.0.0 则开启外网访问
network.host=0.0.0.0
```

# 数据导入

先写到这，明天继续。

# 常用技巧

参考文章：

- https://www.t00ls.net/thread-32593-1-1.html(没有tools的会员，枯了)
- [搭建安全认证的 ELK 日志系统][10]

本文完。

[1]: https://www.elastic.co/cn/
[2]: https://www.elastic.co/cn/downloads/
[3]: https://legacy.gitbook.com/book/chenryn/elk-stack-guide-cn/details
[4]: https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html
[5]: https://img.soapffz.com/archives_img/2019/07/29/archives_20190729_172401.png
[6]: https://img.soapffz.com/archives_img/2019/07/29/archives_20190729_185359.png
[7]: https://img.soapffz.com/archives_img/2019/07/29/archives_20190729_185149.png
[8]: https://img.soapffz.com/archives_img/2019/07/29/archives_20190729_190136.png
[9]: https://img.soapffz.com/archives_img/2019/07/29/archives_20190729_190612.png
[10]: https://www.freebuf.com/articles/security-management/179736.html
