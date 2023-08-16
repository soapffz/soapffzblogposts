---
title: "tinyctf-2014-NaNNaNNaNNaN-Batman-writeup"
categories: [ "CTF" ]
tags: [ "CTF","CTF writeup" ]
draft: false
slug: "11"
date: "2019-01-06 22:37:00"
---

- 为什么要写 2014 年的题的 writeup：因为在做某 CTF 训练平台的题

首先题目给了一个附件，叫做 web100.zip，解压后就是一个 web100 文件

记事本打开是这样的：

![][1]

大部分看得懂，大部分是框框，看到有 script，function 字样，猜测是 php 代码，拖到浏览器中看一看：

![][2]

一个输入框，此时看到末尾是一个执行的 eval 函数：

![][3]

我们把它改为显示 alert 再拖进来看看：

![][4]

欸，乱码没了，得到了 php 源代码：

```
function $(){var e=document.getElementById("c").value;if(e.length==16)if(e.match(/^be0f23/)!=null)if(e.match(/233ac/)!=null)if(e.match(/e98aa$/)!=null)if(e.match(/c7be9/)!=null){var t=["fl","s_a","i","e}"];var n=["a","_h0l","n"];var r=["g{","e","_0"];var i=["it'","_","n"];var s=[t,n,r,i];for(var o=0;o<13;++o){document.write(s[o%4][0]);s[o%4].splice(0,1)}}}document.write('<input id="c"><button onclick=$()>Ok</button>');delete _
```

我们用[工具][5]格式化一下：

![][6]

```
function $(){
	var e=document.getElementById("c").value;
	if(e.length==16)if(e.match(/^be0f23/)!=null)if(e.match(/233ac/)!=null)if(e.match(/e98aa$/)!=null)if(e.match(/c7be9/)!=null){
		var t=["fl","s_a","i","e}"];
		var n=["a","_h0l","n"];
		var r=["g{","e","_0"];
		var i=["it'","_","n"];
		var s=[t,n,r,i];
		for (var o=0;o<13;++o){
			document.write(s[o%4][0]);
			s[o%4].splice(0,1)
		}
	}
}
document.write('<input id="c"><button onclick=$()>Ok</button>');
delete _
```

代码意思很简单，用一个正则表达式，只要输入的字符串以`be0f23`开头，以`e98aa`结尾，中间含有`233ac`、`c7be9`字符串就会执行下面的函数，那么我们构造`be0f233ac7be98aa`字符串回到那个输入框：

![][7]

![][8]

得到 flag：`flag{it's_a_h0le_in_0ne}`

[1]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_223856.png
[2]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_224050.png
[3]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_224302.png
[4]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_224437.png
[5]: http://tools.jb51.net/code/jb51_php_format
[6]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_224721.png
[7]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_225215.png
[8]: https://img.soapffz.com/archives_img/2019/01/06/archives_20190106_225244.png