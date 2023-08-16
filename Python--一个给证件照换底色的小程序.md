---
title: "Python--一个给证件照换底色的小程序"
categories: [ "Python" ]
tags: [ "Python","PyQt5","换背景","AI" ]
draft: false
slug: "321"
date: "2019-07-22 23:38:00"
---

# 起因

看到[一篇文章][1]介绍了一个`AI`抠图的库`removebg`

[点我去 GitHub][2]，点我去[网站官网][3]在线换图片背景

抠图嘛，我也帮朋友干过这事，原来我自己是跟着`doyoudo`的[教程][4]做过，网站上直接看需要注册登录

不想注册的可以到[优酷上看][5]，在这里顺便安利一下[doyoudo][6]这个网站(看到请打钱谢谢)：

> doyoudo 是一个小清新的音视频剪辑软件教程网站

跟着教程熟悉了后大概 10 分钟就能 P 一张图，但是！现在有了这个人工智能抠图的库`removebg`，那肯定要来试一下效果

这个库大概介绍如下：

> 默认生成的图片格式尺寸是标准的，每月最多免费处理 50 张照片。如果想生成高清甚至 4K 或者处理更多图片需要付费。算下来价格大概是 1 元一张。

于是准备用这个核心代码包装一下，继续做一个`PyQt5`的小程序，加强一下我的`PyQt5`功底看下能不能学到一些新东西

# 无 GUI 版本

** 注意：生成的图片会到原图片的目录并且文件名从`图片名.图片后缀`变为`图片名.图片后缀_no_bg.png` **

## 替换背景

注册登录后去[网站 API 接口][7]获取自己的 API，然后用以下几行代码就可实现基本的图片背景替换：

```
from removebg import RemoveBg
rmbg = RemoveBg("你的apikey", "error.log")
rmbg.remove_background_from_img_file(r"C:\Users\soapffz\Desktop\640_2.jpg") # 图片位置
```

效果如下：

![][8]

![][9]

![][10]

为了图片加载速度，这里画质被严重压缩请不要在意。

** 本文用到的这个核心库只有将背景图片背景移除的功能 ** ，填充为其他颜色使用`PIL`里的的`Image`来实现：

## 填充颜色

```
from PIL import Image
img = Image.open(r'640.png').convert("RGBA")
x, y = img.size
card = Image.new("RGBA", img.size, (0, 0, 255))
card.paste(img, (0, 0, x, y), img)
card.save("640_2.jpg", format="png")
```

效果如下：

![][11]

# GUI 版本

** 这里顺便补充下一直在用但一直忘记说的`PyQt5`的部分技巧 **

## 设计 GUI

基础的设计教程都在<<搭建本地 ip 代理池 (完结)>>这篇文章里面，可以在[Python 目录][12]找到这篇文章

GUI 设计图如图所示：

![][13]

## 文件选择

参考文章：[PyQt5 文件对话框 QFileDialog 的使用][14]

选择单个文件：

```
from os import path
from sys import argv

    self.exe_path = path.dirname(argv[0])  # 获取当前程序运行的路径
    self.pushButton.clicked.connect(self.chosepic) # 选择文件的按钮被按下时触发函数

    def chosepic(self):
        # 选择图片
        file_name = QtWidgets.QFileDialog.getOpenFileName(
            self, "选取文件", self.exe_path, "Pic Files (*.png;*.jpg);;Text Files (*.txt)")[0]   # 设置文件扩展名过滤,用双分号间隔
        if file_name == "":
            print("用户取消选择")
            return
        print("你选择的文件为:", file_name)
```

选择单个文件夹：

```
from os import path
from sys import argv

    self.exe_path = path.dirname(argv[0])  # 获取当前程序运行的路径
    self.pushButton.clicked.connect(self.chosedir) # 选择文件夹的按钮被按下时触发函数
    def chosedir(self):
        # 选择含图片的文件夹
        dir_name = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选取文件夹",  self.exe_path)
        if dir_name == "":
            print("\n取消选择")
            return
        print("你选择的文件夹为:", dir_name)
```

这里只介绍了常用的两种，多个文件选择可以使用选择单个文件夹再判断文件后缀的方法来实现，其他方法请参考参考文章。

## 弹框显示实现

### 常用函数：

```
# 信息框
QMessageBox.information(self, '框名', '内容', 按钮s, 默认按钮)
# 问答框
QMessageBox.question(self, '框名', '内容', 按钮s, 默认按钮)
# 警告框
QMessageBox.warning(self, '框名', '内容', 按钮s, 默认按钮)
# 危险框
QMessageBox.ctitical(self, '框名', '内容', 按钮s, 默认按钮)
# 关于框
QMessageBox.about(self, '框名', '内容')
```

实例：

```
from PyQt5.QtWidgets import QMessageBox

# 退出确定框
reply = QMessageBox.question(self, '退出', '确定退出？', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
if reply == QMessageBox.Yes:
	print('退出')
else:
	print('不退出')
```

![][15]

### 自定义消息框

```
# 创建一个问答框，注意是Question
self.box = QMessageBox(QMessageBox.Question, '退出', '确定退出？')

# 添加按钮，可用中文
yes = self.box.addButton('确定', QMessageBox.YesRole)
no = self.box.addButton('取消', QMessageBox.NoRole)

# 设置消息框中内容前面的图标
self.box.setIcon(1)

# 设置消息框的位置，大小无法设置
self.box.setGeometry(500, 500, 0, 0)

# 显示该问答框
self.box.show()

if self.box.clickedButton() == yes:
	print('退出')
else:
	print('不退出')

```

![][16]

参考文章：

- [PyQt5 笔记 5 -- 消息框（QMessageBox）][17]
- [PyQt5 学习笔记（五）：弹出对话框请求确认][18]

## 设置超链接

一般都是在`label`组件上设置，在设计的时候正常填写文字即可，然后需要做如下设置：

```
self.label_getapi.setText("<a href='https://www.remove.bg/api'>点我获取APIKEY:</a>") # 设置超文本文字
self.label_getapi.setOpenExternalLinks(True) # 允许默认浏览器访问超链接
```

## 复选框调用同一个函数检查状态

在我的程序设计中，默认是必须要生成没有背景的颜色的图片，其次才能选择其他背景颜色

那么怎样获取要转换的颜色有哪些呢？可以使用如下方法实现：

```
        self.bg_color_chose_l = []  # 需要转换的颜色有哪些
        self.checkBox_white.stateChanged.connect(self.checkstate)
        self.checkBox_blue.stateChanged.connect(self.checkstate)
        self.checkBox_red.stateChanged.connect(self.checkstate)
        self.pushButton_begin.clicked.connect(self.begin)
    def checkstate(self, state):
        # 用来检测有哪些转换颜色的选项被勾选上了
        # 获取发送信号的checkbox
        which_checkbox = self.sender()
        if state == QtCore.Qt.Unchecked:
            self.insert_msg_to_disp(
                "用户不要{}色背景的图片了".format(which_checkbox.text()))
            self.bg_color_chose_l.remove(which_checkbox.text())
        if state == QtCore.Qt.Checked:
            self.insert_msg_to_disp(
                "用户想要{}色背景的图片".format(which_checkbox.text()))
            self.bg_color_chose_l.append(which_checkbox.text())
        if len(self.bg_color_chose_l) == 0:
            self.insert_msg_to_disp("现在未选择任何背景!")
        else:
            self.insert_msg_to_disp(
                "现在用户想要的背景颜色有：{}".format(self.bg_color_chose_l)
```

效果如下：

![][19]

参考文章：[PyQt5 笔记 - CheckBox][20]

## 刷新页面

在程序可能会卡顿的地方尤其是`for`循环的第一句话添加这一行命令：

```
QtWidgets.QApplication.processEvents()
```

## 最终效果

** 注意，在实际使用时发现当图片的背景过于复杂时不能成功清除背景 **

** 会在`error.log`中报如下错：**

```
ERROR:root:Unable to save C:\Users\soapffz\Desktop\xdx.jpg_no_bg.png due to could not identify foreground in image. for details and recommendations see https://www.remove.bg/supported-images.
```

** 所以，不要选择过于复杂的图片来实验，尽量就选择背景不那么复杂的人像 **

单个文件转换最终效果如下：

![][21]

多个文件转换最终效果如下：

![][22]

本文完。(熬夜爆肝到 2 点半)

---

成品下载链接(以后更新会放在这里)：

(2019-07-24 凌晨 2 点半)：https://www.lanzous.com/i54q96f

[1]: https://mp.weixin.qq.com/s/8R4AliVJ8uiqSirgdkpEbA
[2]: https://github.com/brilam/remove-bg
[3]: https://www.remove.bg/
[4]: http://www.doyoudo.com/video/215
[5]: https://v.youku.com/v_show/id_XMTU4NDc1NTkxMg==.html
[6]: http://www.doyoudo.com/
[7]: https://www.remove.bg/api
[8]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190723_204043.jpg
[9]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190723_204101.png
[10]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190723_204122.gif
[11]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190723_225907.gif
[12]: https://soapffz.com/python
[13]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190724_002702.png
[14]: https://blog.csdn.net/humanking7/article/details/80546728
[15]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190723_231912.png
[16]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190723_232014.png
[17]: https://blog.csdn.net/wang_jiankun/article/details/83269859
[18]: https://www.jianshu.com/p/8fc44cea9bd8
[19]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190724_005004.gif
[20]: https://blog.csdn.net/john_lan_2008/article/details/76713495
[21]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190724_020346.gif
[22]: https://img.soapffz.com/archives_img/2019/07/22/archives_20190724_022025.gif