# crawler3

## 介绍

这是个人的爬虫集合项目，主要以招聘、职业规划发现等为主  
python：3.6  
项目进度：

```html
- [已完成]51job职位多线程爬取excel版本
- [已完成]51job职位多线程爬取mysql版本
```

## QuickStart
### 安装
1.安装mysql
```bash
yum list "mariadb*" # 查看包
yum install mariadb-server -y # 安装
systemctl start mariadb # 启动,停止使用stop
systemctl enable mariadb # 开机启动
```

2.设置密码
```bash
mysql # 进入命令行
set password for root@127.0.0.1 = password('12345'); # 设置root密码为12345
mysql -uroot -p12345 # 使用新密码进入
create database crawler # 创建爬虫数据存储数据库，表会自动创建的
```

3. 安装python3
```bash
yum install python3
python3 -m pip install xlwt  # excel
python3 -m pip install pymysql # mysql
```

4.安装tmux
```bash
yum install tmux # 关闭终端后，该进程不会退出，后台继续运行
```

### 运行

1.首次运行
```bash
tmux  # 启动一个后台任务终端
cd /
mkdir data
cd /data
git clone https://github.com/xmcy0011/crawler3.git
cd crawler3
python3 jobMysql.py
```

2.查看上次运行结果
```bash
tmux ls # 查看任务列表
tmux attach 0 # 附加进程，可以看到上次的运行结果
exit # 退出tmux终端
```

3.导出
```bash
mysqldump -hlocalhost -P3306 -uroot -p12345 --database crawler | gzip > /data/crawler3/51job/crawler2020-07-20.sql.gz
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
