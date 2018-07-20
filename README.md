# crawler3

## 介绍

这是个人的爬虫集合项目，主要以招聘、职业规划发现等为主  
python：3.6  
项目进度：

```html
- [已完成]51job职位多线程爬取excel版本
- 51job职位多线程爬取mysql版本
```

## 爬取思路简介

善用正则表达式.\*?

- “.”：匹配除“\n”和"\r"之外的任何单个字符。要匹配包括“\n”和"\r"在内的任何字符，请使用像“[\s\S]”的模式。
- “\*”：匹配前面的子表达式任意次。例如，zo*能匹配“z”，也能匹配“zo”以及“zoo”。*等价于{0,}。
- “?”：匹配前面的子表达式零次或一次。例如，“do(es)?”可以匹配“do”或“does”。?等价于{0,1}。

如要匹配：

```html
<div class="el">
    <p class="t1 ">
        <em class="check" name="delivery_em" onclick="checkboxClick(this)"></em>
        <input class="checkbox" type="checkbox" name="delivery_jobid" value="98220269" jt="6" style="display:none">
        <span>
            <a target="_blank" title="移动产品经理/主管（浦东张江）" href="http://51rz.51job.com/sc/show_job_detail.php?jobid=98220269" onmousedown="jobview('98220269');">
                移动产品经理/主管（浦东张江）                                </a>
        </span>
                                                            </p>
    <span class="t2"><a target="_blank" title="“前程无忧”51job.com（上海）" href="http://51rz.51job.com/company.php?company=1249">“前程无忧”51job.com（上海）</a></span>
    <span class="t3">上海-浦东新区</span>
    <span class="t4"></span>
    <span class="t5">07-20</span>
</div>
```

则正则为：

```python
# 要抓取的部分写(.*?)，特别注意"</span>"和"<span>"之间是有换行符的，所有要写.*?
# 职位 职位url 公司名 工作地点 薪资 发布时间
reg = re.compile(r'class="t1 ">.*? <a target="_blank" title="(.*?)" href="(.*?)".*? <span class="t2"><a target="_blank" title="(.*?)".*?<span class="t3">(.*?)</span>.*?<span class="t4">(.*?)</span>.*? <span class="t5">(.*?)</span>', re.S)  # 匹配换行符
```

可以在这里观察：  
[https://tool.lu/regex/](https://tool.lu/regex/)  
**提示：请勾选“单行”**

## 预览

![爬取列表](https://github.com/xmcy0011/crawler3/blob/master/Resources/Demo/2018.7已爬取示例.jpg)  

![产品经理示例](https://github.com/xmcy0011/crawler3/blob/master/Resources/Demo/2018.7产品经理.jpg)

## License

[Apache License 2.0](https://github.com/xmcy0011/crawler3/blob/master/LICENSE)

## 特此声明

仅供学习，请勿用于商业用途。
