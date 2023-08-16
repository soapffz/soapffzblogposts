---
title: "Python--高德地图api批量查询原图地理位置"
categories: [ "Python" ]
tags: [ "Python","PyQt5","GPS","地理位置" ]
draft: false
slug: "383"
date: "2019-08-28 09:36:00"
---

# 事情起因

很多媒体都报道过在社交媒体聊天时，发送图片如果勾选到“原图”选项，

则有可能根据图片中携带的 GPS 信息暴露个人位置隐私

那么你有没有想过自己动手实现查询地理位置信息呢？

今天刚好看到一篇文章，复现一下

# 申请 key

首先注册并登录进[高德开放平台][1]

创建一个应用并点击右边的`+`号申请`key`：

![][2]

给`key`取个名称并选择`web服务`提交：

![][3]

得到了逆地理编码的`API`：

![][4]

通过 GPS 获取的经度、纬度和高德地图的坐标存在一定的误差，高德官方提供了坐标转换的方法

用的`key`也是属于这个`WEB`服务，所以不用再申请，这个`key`会被使用到两次

# 图片处理

使用`exifread`库读取图片的`exif`信息，官方[GitHub][5]有常见参数获取方法

先用`pip`安装：

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple exifread
```

基本使用方法如下：

```
with open("test.jpg", 'rb') as f:
    image_exif = exifread.process_file(f)
    for tag, value in image_exif.items():
        print(tag, value)
```

这是为了打印出所有的信息才这样使用，实际上`exif`读出来即`dict`，直接键值方式读就可以，没必要`for`循环

(** 这里说明一下，如果你想测试一下，用自己的手机拍张照片来测试，使用微信和 QQ 上传到电脑的图片是无效的 **

可以通过`手机自带相机拍照` -> `通过网盘或文件快传等方式传输`,例如，可使用[奶牛快传][6])

但是这里参数太多了，大部分不需要，我们只需要获取以下信息：

```
Image Make:手机品牌
Image Model：手机型号
EXIF LensModel:摄像头信息
GPS GPSLongitudeRef:经度标志
GPS GPSLongitude:经度
GPS GPSLatitudeRef:纬度标志
GPS GPSLatitude:纬度
其中
写程序时经度和维度都以N方向为正值
```

# GPS 转高德

我们从图片中读取到的 GPS 信息还是不太恰当的，高德`api`提供了[转换功能][7]

也是使用相同的`api`去构造函数并请求即可：

![][8]

# 查询

获得高德坐标之后使用相同的`api`再构造一个`url`可以对`gps`请求`逆地理编码转换`

将`gps`坐标转换为街道地址

全代码如下：

```
# -*- coding: utf-8 -*-
'''
@author: soapffz
@fucntion: 用高德地图api查询原图信息和地理位置(可单张或文件夹批量)
@time: 2019-09-03
'''

from os import path, listdir
import exifread
import requests
import json


"""
如果提示库未安装，请参考：
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple exifread
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple json

高德开放平台：https://lbs.amap.com/dev/key/app
文章教程：https://soapffz.com/383.html

如果批量查询建议放到一个文件夹内，初始化时填写文件夹路径
"""


class Location_query(object):
    def __init__(self, key, img_path):
        # 传入参数，申请到的高德api和图片路径(也可能是文件夹路径)
        self.key = key
        if len(self.key) != 32:
            print("你的key好像不对，大兄弟...")
            exit(0)
        self.img_path = img_path
        self.judge_dir()

    def judge_dir(self):
        # 判断是否为文件夹
        if path.isdir(self.img_path):
            print("你选择的是一个文件夹")
            self.pic_l = []
            for item in listdir(self.img_path):
                if path.splitext(item)[1].lower() in [".jpg", ".png", ".jpeg"]:
                    self.pic_l.append(path.join(self.img_path, item))
            if len(self.pic_l) == 0:
                print("你选的文件夹里面一张图片都没有，查你大爷")
                exit(0)
            elif len(self.pic_l) == 1:
                self.singal_image_info(self.pic_l[0])
            else:
                print("共获取到{}张图片\n".format(len(self.pic_l)))
                self.multi_pics_query()
        else:
            self.singal_image_info(self.img_path)

    def singal_image_info(self, img):
        # 单张图片查询
        if type(img) != "list":
            image_l = []
            image_l.append(img)
        else:
            image_l = img
        singal_pic_info_d = self.get_image_info(image_l)
        for key, value in singal_pic_info_d.items():
            print(key)
            for info in value:
                print(info)

    def multi_pics_query(self):
        # 处理多张图片，由于逆地理编码一次只能处理20对坐标，所以把所有坐标按每20个切割为一个列表
        cut_pic_l = [self.pic_l[i:i + 20]
                     for i in range(0, len(self.pic_l), 20)]
        info_l = {}  # 存储所有的查询信息
        for cut in cut_pic_l:
            batch_info = self.get_image_info(cut)
            info_l = {**info_l, **batch_info}
        for key, value in info_l.items():
            print(key)
            for info in value:
                print(info)
            print("\n")

    def parse_gps_express(self, gps_express):
        """
        GPS坐标值转数值
        :param gps_express:GPS坐标表达式 [1,2,3/4]
        :return: GPS坐标数值 1.035542
        """
        try:
            express = str(gps_express).replace(
                " ", "").replace("[", "").replace("]", "")
            parts = express.split(",")
            subpart = parts[2].split("/")
            degress = float(parts[0])
            minutes = float(parts[1])
            seconds = float(subpart[0]) / float(subpart[1])
            return degress + minutes / 60 + seconds / 3600
        except:
            raise Exception("图片信息错误")

    def get_image_info(self, images):
        """
        照片拍摄地GPS坐标
        :param photo_path: 多张照片的磁盘路径(为了配合逆地理编码api一次只能查询20对，这里也设置为最多20张图片)
        :return: 多张照片的详细信息 （手机品牌，手机型号，摄像头信息，地理位置）
        """
        multi_image_info = {}  # 存储图片的信息，键为图片，值为图片的信息
        gps_coordinates = {}  # 存储多个gps信息批量查询，避免查询次数的浪费，键为图片，值为gps值
        for image in images:
            singal_image_info = []
            image_name = image.split("\\")[-1]
            with open(image, 'rb') as f:
                image_exif = exifread.process_file(f)
            if "Image Make" in image_exif.keys():
                # 如果手机信息存在，则获得图片的手机信息
                singal_image_info.append(
                    "手机品牌为:{}".format(str(image_exif["Image Make"])))
                singal_image_info.append("手机型号为:{}".format(
                    str(image_exif["Image Model"])))
                singal_image_info.append("摄像头信息为:{}".format(
                    str(image_exif["EXIF LensModel"])))
            else:
                singal_image_info.append("未获取到手机信息")
            if "GPS GPSLongitudeRef" in image_exif.keys():
                # 如果GPS信息存在，获得图片的GPS信息
                #longitude_ref = str(image_exif["GPS GPSLongitudeRef"]).strip()
                longitude = self.parse_gps_express(
                    str(image_exif["GPS GPSLongitude"]))
                #latitude_ref = str(image_exif["GPS GPSLatitudeRef"]).strip()
                latitude = self.parse_gps_express(
                    str(image_exif["GPS GPSLatitude"]))
                #lng = longitude if "E" == longitude_ref else 0 - longitude
                #lat = latitude if "E" == latitude_ref else 0 - latitude
                gps_coordinates[image] = str(longitude) + "," + str(latitude)
                # ["116.487585177952,39.991754014757","116.487585177952,39.991653917101"]
            else:
                singal_image_info.append("未获取到gps信息")
            multi_image_info[image] = singal_image_info
        for image, location in zip(gps_coordinates.keys(), self.convert_gps(gps_coordinates.values())):
            multi_image_info[image].append("位置为:{}".format(location))
        return multi_image_info

    def convert_gps(self, gps_coordinates):
        """
        坐标转换：GPS转高德
        :param gps_coordinates: 多个位置"GPS经度,GPS纬度"的集合(元组或数组都可以)
        :return: 多个位置"高德经度,高德纬度"的集合列表，最多一次接收40对坐标
        """
        try:
            coordinates = "|".join(gps_coordinates)
            url = "https://restapi.amap.com/v3/assistant/coordinate/convert?key={0}&locations={1}&coordsys=gps&output=json".format(
                self.key, coordinates)
            response = requests.get(url)
            result = json.loads(response.text)
            if "1" == result["status"]:
                gd_coordinates = result["locations"].split(";")
                return self.get_map_address((gd_coordinates))
            else:
                print("error:", result["infocode"], result["info"])
        except Exception as e:
            raise e

    def get_map_address(self, gd_coordinates):
        """
        逆地理编码（高德坐标转地址）
        :param gd_coordinates:多个位置"高德经度,高德纬度"的集合(元组或数组都可以)
        :return:多个位置地址信息的列表，最多一次查询20个经纬度点
        """
        try:
            coordinates = "|".join(gd_coordinates)
            batch = "true" if len(gd_coordinates) > 1 else "false"
            url = "https://restapi.amap.com/v3/geocode/regeo?key={0}&location={1}&batch={2}&radius=500&extensions=base&output=json".format(
                self.key, coordinates, batch)
            response = requests.get(url)
            result = json.loads(response.text)
            if "1" == result["status"]:
                address = []
                if batch == "true":
                    address.extend([add["formatted_address"]
                                    for add in list(result["regeocodes"])])
                else:
                    fmt_add = result["regeocode"]["formatted_address"]
                    address.append(fmt_add)
                return address
            else:
                print(result)
        except Exception as e:
            raise e


if __name__ == "__main__":
    key = ""  # 填写你申请到的高德开放平台api
    img_path = ""  # 填写图片或者文件夹地址
    Location_query(key, img_path)
```

单个图片查询效果如下：

![][9]

文件夹查询效果如下：

![][10]

---

**代办**

其中有一个地方没搞清楚，就是从图片读取到的 gps 信息：`longitude`和`latitude`

这两个`longitude_ref`和`latitude_ref`的关系，从参考文章里看到的是如果方向是`N`需要转为负数

但是负数是不符合高德地图 gps 规范的，不加负号是能查询出来的，所以这两行注释掉了，暂时没看懂

# EXIF 查看软件

查资料的时候看到的 ，感觉还不做，从`zdfan`上找到一个最新的[破解版][11]，实测能用

也可以看到我们查询的效果是正确的：

![][12]

本文完。

参考文章：

- [我背着女朋友，用 Python 偷偷抓取了她的行踪][13]
- [地理/逆地理编码-API 文档-开发指南-Web 服务 API | 高德地图 API][14]
- [《GPS 坐标转换高德坐标方法说明》][15]
- [《高德关于访问流量限制的说明》][16]
- [利用 Python 读取图片 exif 敏感信息][17]
- [照片的 GPS 位置信息读取][18]

[1]: https://lbs.amap.com/dev/index
[2]: https://img.soapffz.com/archives_img/2019/08/28/archives_20190828_093003.png
[3]: https://img.soapffz.com/archives_img/2019/08/28/archives_20190828_093101.png
[4]: https://img.soapffz.com/archives_img/2019/08/28/archives_20190902_160051.png
[5]: https://github.com/ianare/exif-py
[6]: https://cowtransfer.com/
[7]: https://lbs.amap.com/api/webservice/guide/api/convert
[8]: https://img.soapffz.com/archives_img/2019/08/28/archives_20190904_093649.png
[9]: https://img.soapffz.com/archives_img/2019/08/28/archives_20190904_094140.png
[10]: https://img.soapffz.com/archives_img/2019/08/28/archives_20190904_094738.png
[11]: http://www.zdfans.com/html/29679.html
[12]: https://img.soapffz.com/archives_img/2019/08/28/archives_20190904_095651.png
[13]: https://mp.weixin.qq.com/s/czXYeK7sRpIJssQ9Ga13Ww
[14]: https://lbs.amap.com/api/webservice/guide/api/georegeo
[15]: https://lbs.amap.com/api/webservice/guide/api/convert
[16]: https://lbs.amap.com/api/webservice/guide/tools/flowlevel
[17]: https://www.cnblogs.com/sevck/p/10942219.html
[18]: https://blog.csdn.net/maozexijr/article/details/92790722