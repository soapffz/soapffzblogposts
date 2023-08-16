---
title: "Python-基于socket实现FTP基本功能"
categories: [ "Python" ]
tags: [ "Python","socket","PyQt5" ]
draft: false
slug: "311"
date: "2019-07-13 11:42:00"
---

# 起因

来源于学期结束的计算机网络课程设计，原题目是基于 DELPHI 实现 FTP 协议的相关功能

既然可以随意选择语言，那我就使用世界上最好的`Python`了(不接受反驳)#(脸红)

本篇文章将根据参考文章复现一下基于`socket`通信的交流软件

** 由于基于 socket 通信的部分不是太难，本篇将不做过多解释 **

参考文章：

- [一小时学会用 Python Socket 开发可并发的 FTP 服务器！][1]

# 最简单的 socket 通信

`server`端代码如下：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 简单的socket通信(服务端)
@time: 2019-07-07
'''

import socket
host = ''
port = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 生成socket tcp通信实例，
s.bind((host, port))  # 绑定ip和端口，注意bind只接受一个参数，(host,port)做成一个元组传进去
s.listen(5)  # 开始监听，里面的数字是代表服务端在拒绝新连接之前最多可以挂起多少连接，不过实验过了没啥用，所以写个1就好了

while True:
    conn, addr = s.accept()  # 接受连接，并返回两个变量，conn代表每个新连接进入后服务端都会为生成一个新实例，后面可以用这个实例进行发送和接收，addr是连接进来的客户端的地址，accept()方法在有新连接进入时就会返回conn,addr这两个变量，但如果没有连接时，此方法就会阻塞直至有新连接过来。

    print('Connected by', addr)
    while True:
        data = conn.recv(1024)  # 接收1024字节数据
        if not data:
            break  # 如果收不到客户端数据了(代表客户端断开了)，就断开
        print("收到消息：", data)
        conn.sendall(data.upper())  # 将收到的数据全变成大写再发给客户端
    conn.close()  # 关闭连接
```

`client`端：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 简单的socket通信(客户端)
@time: 2019-07-07
'''

import socket
host = '192.168.2.1'  # 远程socket服务器ip
port = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 实例化socket
s.connect((host, port))  # 连接socket服务器

while True:
    msg = input("Please input:\n").strip().encode('ascii')
    s.sendall(msg)  # 向服务器发送消息
    data = s.recv(1024)  # 接受服务器的消息

    print("Recevied:", data)
s.close()
```

演示效果如下：

![][2]

# SocketServer 多线程版

当我们同时启动 2 个客户端，发现只能有一个客户端跟服务端不断的通信，另一个客户端会一直处在挂起状态

当把可以通信的客户端断开后，第 2 个客户端就可以跟服务端进行通信了。

为了让服务端口可以同时为与多个客户端进行通信,我们调用一个叫 SocketServer 的模块

`server`端代码：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 简单的socket通信(服务端)
@time: 2019-07-07
'''

import socketserver


class MyTCPHandler(socketserver.BaseRequestHandler):
    # 继承BaseRequestHandler基类，然后必须重写handle方法，并且在handle方法里实现与客户端的所有交互
    def handle(self):
        while True:
            data = self.request.recv(1024)  # 接收1024字节数据
            if not data:
                break
            print("收到消息：", data)
            self.request.sendall(data.upper())


if __name__ == "__main__":
    host, port = "localhost", 50007

    # 把刚才写的类当作一个参数传给ThreadingTCPServer这个类，下面的代码就创建了一个多线程socket server
    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    # 启动这个server,这个server会一直运行，除非按ctrl+c停止
    server.serve_forever()
```

`client`代码：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 简单的socket通信(客户端)
@time: 2019-07-07
'''

import socket
host = 'localhost'  # 远程socket服务器ip
port = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 实例化socket
s.connect((host, port))  # 连接socket服务器

while True:
    msg = input("Please input:\n").strip().encode('ascii')
    s.sendall(msg)  # 向服务器发送消息
    data = s.recv(1024)  # 接受服务器的消息

    print("Recevied:", data)
s.close()
```

演示效果如下：

![][3]

# 模拟实现 ftpserver

`server`端代码如下：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 简单的socket通信实现ftp传输(服务端)
@time: 2019-07-07
'''

import socketserver
import os


class MYTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        instruction = self.request.recv(
            1024).strip().decode("ascii")  # 接收客户端命令
        if not instruction:
            exit(0)
        # 将客户端发过来消息拆分，消息类似这种格式""FileTransfer|get|file_name"
        instruction = instruction.split("|")
        if hasattr(self, instruction[0]):  # 判断类中是否有这个方法
            func = getattr(self, instruction[0])  # 获取这个方法的内存对象
            func(instruction)  # 调用此方法

    def FileTransfer(self, msg):  # 负责文件的发送和接收
        print("--filetransfer--", msg)
        if msg[1] == "get":
            print("client wants to download file:", msg[2])
            if os.path.isfile(msg[2]):  # 判断客户端发的文件名是否存在并是个文件
                file_size = os.path.getsize(msg[2])  # 获取文件大小
                res = "ready|{}".format(file_size)  # 把文件大小告诉客户端
            else:
                res = "file not exist"  # 文件也有可能不存在
            send_confirmation = "FileTransfer|get|{}".format(
                res).encode("ascii")
            self.request.send(send_confirmation)  # 发送确认消息给客户端
            # 等待客户端确认，如果这时不等客户端确认就立刻给客户端发文件内容，因为为了减少IO操作，socket发送和接收是有缓冲区的，缓冲区满了才会发送，那上一条消息很有可能会和文件内容的一部分被合并成一条消息发送给客户端，这就形成了粘包，所以这里等待客户端的一个确认消息，就把两次发送分开了，不会再有粘包
            feedback = self.request.recv(100)
            if feedback == "FileTransfer|get|recv_ready":  # 如果客户端说准备好接收了
                with open("{}".format(msg[2], 'rb')) as f:
                    size_left = file_size
                    while size_left > 0:
                        if size_left < 1024:
                            # 剩下的部分小于1024个字节就直接传输
                            self.request.sendall(f.read(size_left))
                            size_left = 0
                        else:
                            # 剩下的部分大于1024个字节就一次传输1024个字节
                            self.request.sendall(f.read(1024))
                            size_left -= 1024
                    print("--send file:{}done".format(msg[2]))


if __name__ == "__main__":
    host, port = "", 9002
    server = socketserver.ThreadingTCPServer((host, port), MYTCPHandler)
    server.serve_forever()
```

`client`端：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 简单的socket通信实现ftp传输(客户端)
@time: 2019-07-07
'''

import socket
import os


class FTPClient(object):
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))  # 连接服务器

    def start(self):  # 实例化客户端类后，需要调用此方法启动客户端
        self.interactive()

    def interactive(self):
        while True:
            user_input = input(">>.").strip()
            if len(user_input) == 0:
                continue
            user_input = user_input.split()  # 用户输入的指令进行拆分，第一个参数是指要进行什么动作，比如get remote_filename
            if hasattr(self, user_input[0]):  # 判断类中是否有get或其他输入的方法
                func = getattr(self, user_input[0])  # 通过字符串获取类中对应方法的内存对象
                func(user_input)  # 调用此内存对象
            else:
                print("Wrong cmd usage")

    def get(self, msg):  # 从服务器端下载文件
        print("---get func---", msg)
        if len(msg) == 2:
            file_name = msg[1]
            instruction = "FileTransfer|get|{}".format(
                file_name).encode("ascii")  # 告诉服务器端要下载什么文件
            self.sock.send(instruction)
            feedback = self.sock.recv(100).decode("ascii")  # 等待服务器端的消息确认
            print("-->", feedback)
            # 代表服务器上文件存在，并且服务器已经准备好了发送此文件到客户端
            if feedback.startswith("FileTransfer|get|ready"):
                # 服务器端发回来的确认消息中，最后面一个值是文件大小，必须知道文件大小才知道 一共要收多少内容
                file_size = int(feedback.split("|")[-1])
                self.sock.send("FileTransfer|get|recv_ready".encode(
                    "ascii"))  # 告诉服务器端已经准备好了接收
                recv_size = 0  # 因为 文件可能比较大，一次收不完，所以要循环收，每收到一次，就计个数
                # 在本地创建一个新文件来存这个要下载的文件内容
                with open("client_recv/{}".format(os.path.basename(file_name)), 'wb') as f:
                    print("__>", file_name)
                    recv_size = 0
                    while recv_size != file_size:
                        if file_size - recv_size > 1024:
                            data = self.sock.recv(1024)
                        else:
                            data = self.sock.recv(file_size - recv_size)
                        recv_size += len(data)
                        f.write(data)
                    print("--recv file:{}".format(file_name))
            else:
                print(feedback)
        else:
            print("\033[31;1mWrong cmd usage\033[0m")


if __name__ == "__main__":
    f = FTPClient("localhost", 9002)
    f.start()
```

效果如下：

![][4]

到这里为之，`socket`的部分我们已经大概了解的差不多了，接下来就是设计好 GUI 并同时设计逻辑了

# 课设设计

由于使用`socketserver`库时需要使用`server.serve_forever()`语句来保持服务器的运行

而在`GUI`的运行中，也需要使用`sys_exit(app.exec_())`语句来保持界面的运行

这两条语句都类似于`While True`，是一直在内部循环的，所以先使用了哪个循环

就会一直在这个循环中运行，不能运行后面的代码

直接导致的缺陷就是，服务器端和`GUI`不能同时运行，所以最后我放弃了`server`端的`GUI`界面

`PyQt5`的教程在`搭建本地 ip 代理池 (完结)`这篇文章的 UI 设计部分已经介绍过

我们这里来补充一些

先来一张`UI`设计图：

![][5]

如同我在搭建本地搭建代理池的文章中说的一样，每一个部分都强烈建议用`Frame`框架包起来

当然，最上面登陆区为了对齐的的时候方便，我使用了两个`Frame`

分完区放置完部件，就把需要用到的按钮修改常用名，然后按照代理池文章中介绍的`UI与代码逻辑分离`操作就可以开始写代码了

下面介绍这次使用`PyQt5`中遇到的几个小问题

## 进度条

第一次接触到进度条，觉得效果还可以，不过没找到太多设置的方法，只有一个

`setRange`设置范围和`setValue`，不过这两个也足够了，我的用法如下：

```
# 设置进度条的范围
self.progressBar.setRange(0, 1)

# 在用的地方插入
self.progressBar.setValue(int(recv_size / file_size))
```

`socket`在本地传输文件超级快，完全看不出效果，后面效果演示的时候大家可以看下速度

## Qt5Core.dll 缺失

这次在打包的时候遇到的问题，全新的`Python`安装环境

按顺序`pip install`了`pipreqs,PyQt5,pyinstaller`等库之后

打包的时候非说`Qt5Core.dll`文件缺失，而且在系统文件中是搜不到的

于是在网上找到了一个老哥提供的下载，安全性未知，反正我可以用

[点我去下载][6]，下载后放到系统环境变量有的位置即可，比如：

```
C:\Windows\System32
C:\
C:\Anaconda
```

即可。

---

更新，我在`csdn`下载的时候这个文件还不需要积分，现在需要了，我把我下载下来的[传一份][7]

## 打包后的图标不显示的问题

本来这个我在写本地代理池的时候就遇到了，但是当时给忘了，这里补上

1.创建 qrc 文件，写入以下内容(注意代码格式过了就会直接报错)：

```
<RCC>
  <qresource prefix="/">
    <file>favicon.ico</file>
  </qresource>
</RCC>
```

2.生成 py 文件，这个 py 文件把图片保存成二进制：

```
pyrcc5 -o image.py image.qrc
```

3.导入模块，设置图标

```
import image
MainWindow.setWindowIcon(QtGui.QIcon(':/favicon.ico'))
```

即在原来的图标名字前加上;/即可

## 加盐的哈希库

为了能在老师验收的时候加一个噱头，`client`端加密时使用加密哈希加密传输

`server`端收到用户名和哈希值后先判断用户名是否在数据库中，然后使用解密算法

将传输的哈希与数据库中的明文密码作比较

参考文章：[python 中使用加盐哈希函数加密密码][8]

安装：`pip install werkzeug`

`client`端加密使用`generate_password_hash`函数

```
generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

password 为明文密码
method 哈希的方式,格式为 pbpdf2:<method> 主要有sha1,sha256,md5
salt_length 盐值的长度，默认为8
```

一般后面两个参数都可以缺省，直接使用就好

`server`端解密使用`check_password_hash`

```
check_password_hash(pwhash, password)

pwhash 为密文
password 为明文

相同则返回True，不同返回 False
```

## 最终效果演示

1.登录注销

![][9]

2.目录操作

![][10]

3.下载

![][11]

4.上传

![][12]

5.删除

![][13]

本文完。

[1]: https://blog.51cto.com/3060674/1687308
[2]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_150041.png
[3]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_152836.png
[4]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_154932.png
[5]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_155538.png
[6]: https://download.csdn.net/download/kingdom54/10314240
[7]: https://www.lanzous.com/i5tn51i
[8]: https://www.yangyanxing.com/article/python_generate_password_hash.html
[9]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_171113.gif
[10]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_171130.gif
[11]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_173133.gif
[12]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_173158.gif
[13]: https://img.soapffz.com/archives_img/2019/07/13/archives_20190713_173419.gif