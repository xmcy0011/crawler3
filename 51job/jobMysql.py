# -*- coding:utf-8 -*-
import socket
import urllib.request
import re
import xlwt  # 用来创建excel文档并写入数据
import pymysql  # mysql
import threading  # 多线程抓取
from urllib.parse import quote
import datetime
import ssl

def url_config(jobName):
    # 北上广深杭 不限行业
    url = "https://search.51job.com/list/020000%252C010000%252C030200%252C040000%252C080200,000000,0000,00,9,99,"
    # 具体的搜索关键词，注意要进行2次url编码
    url += quote(quote(jobName, 'utf-8'), 'utf-8') + ",2,"

    #
    # 一下是一些范例
    #

    # java
    # url = 'https://search.51job.com/list/020000%252C010000%252C030200%252C040000%252C080200,000000,0000,00,9,99,java,2,1.html'
    # c# 北上广深杭 不限行业
    # url = 'https://search.51job.com/list/020000%252C010000%252C030200%252C040000%252C080200,000000,0000,00,9,99,c%2523,2,1.html'
    # c/c++
    # url = 'https://search.51job.com/list/020000%252C010000%252C030200%252C040000%252C080200,000000,0000,00,9,99,c%252Fc%252B%252B,2,1.html'
    # html
    # python
    # php
    # javascript
    # android
    # url = 'https://search.51job.com/list/020000%252C010000%252C030200%252C040000%252C080200,000000,0000,00,9,99,android,2,1.html'
    # ios
    # url = 'https://search.51job.com/list/020000%252C010000%252C030200%252C040000%252C080200,000000,0000,00,9,99,ios,2,1.html'
    # 大数据
    # url = 'https://search.51job.com/list/020000%252C010000%252C030200%252C040000%252C080200,000000,0000,00,9,99,%25E5%25A4%25A7%25E6%2595%25B0%25E6%258D%25AE,2,1.html'
    # 产品经理
    # url = 'https://search.51job.com/list/020000%252C010000%252C030200%252C040000%252C080200,000000,0000,00,9,99,%25E4%25BA%25A7%25E5%2593%2581%25E7%25BB%258F%25E7%2590%2586,2,1.html'
    # 项目经理
    # 人工智能
    # 物联网
    # 区块链
    # VR/AR
    # 新能源
    return url


def get_content(jobName, page):  # 获取原码
    url = url_config(jobName) + str(page) + '.html'
    context = ssl._create_unverified_context() 
    a = urllib.request.urlopen(url,context=context)  # 打开网址
    html = a.read().decode('gbk')  # 读取源代码并转为unicode
    return html


def get_total_count(html):
    reg = re.compile(
        r'<div class="sbox">.*?</div>.*?<div class="rt">(.*?)</div>', re.S)
    items = re.findall(reg, html)
    if len(items) >= 0:
        return items[0]
    return 0


def get(html):
    # 职位 职位url 公司名 工作地点 薪资 发布时间
    reg = re.compile(r'<p class="t1 ">.*? <a target="_blank" title="(.*?)" href="(.*?)".*? <span class="t2"><a target="_blank" title="(.*?)".*?<span class="t3">(.*?)</span>.*?<span class="t4">(.*?)</span>.*? <span class="t5">(.*?)</span>', re.S)  # 匹配换行符
    items = re.findall(reg, html)
    return items


def get_job_desc(url):  # 获取职位描述
    context = ssl._create_unverified_context()
    a = urllib.request.urlopen(url,context=context)  # 打开网址
    html = a.read().decode('gbk')  # 读取源代码并转为unicode
    items = []

    # 该公司所有职位URL 公司类型 公司规模 公司行业
    reg = re.compile(r'<div class="com_tag">.*?<p class="at" title="(.*?)">.*?<p class="at" title="(.*?)">.*?<p class="at" title="(.*?)">.*?<a track-type="jobsButtonClick" event-type="2" class="icon_b i_house" href="(.*?)".*?</div>', re.S)
    temp = re.findall(reg, html)
    if len(temp) == 0:
        temp.append('')
        temp[0] = ['', '', '', '']
    for item in temp[0]:
        items.append(item.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", ""))

    # 学历 经验 招聘人数
    reg = re.compile(r'<p class="msg ltype" title="(.*?)">', re.S)
    # 广州-天河区&nbsp;&nbsp;|&nbsp;&nbsp;2年经验&nbsp;&nbsp;|&nbsp;&nbsp;招1人&nbsp;&nbsp;|&nbsp;&nbsp;09-07发布
    temp = re.findall(reg, html)[0]
    temp = temp.split('&nbsp;&nbsp;|&nbsp;&nbsp;')
    if len(temp) == 4: 
        # 区域 经验 招聘人数 发布时间
        items.append('')
        items.append(temp[1])
        items.append(temp[2])
    else:
        # 区域 经验 学历 招聘人数 发布时间
        items.append(temp[2])
        items.append(temp[1])
        items.append(temp[3])

    # 福利标签（可为空）
    reg = re.compile(r'<div class="jtag">.*?<div class="t1">(.*?)<div class="clear"></div>.*?</div>', re.S)
    temp = re.findall(reg, html)
    if len(temp) > 0:
        welfare = temp[0].replace("\r", "").replace("\n", "").replace("\t", "")
        if welfare.strip() == '':
            items.append("")
        else:
            items.append(welfare.replace(" ", "").replace("\"","\'"))
    else:
        items.append("")

    # 职位描述
    reg = re.compile(r'<div class="bmsg job_msg inbox">(.*?)<div class="mt10">', re.S)
    temp = re.findall(reg, html)[0]
    items.append(temp.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", ""))

    # 职能类别
    reg = re.compile(r'<div class="mt10">.*?<p class="fp">.*?<span class="label">职能类别：</span>.*?<a.*?>(.*?)</a>.*?</p>', re.S)
    temp = re.findall(reg, html)[0]
    items.append(temp.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "").replace(r'<spanclass="el">', "").replace("</span>", " "))

    # 公司地址 公司信息
    reg = re.compile(r'<p class="fp">.*?<span class="label">上班地址：</span>(.*?)</p>.*?<div class="tmsg inbox">(.*?)</div>', re.S)
    temp = re.findall(reg, html)
    if len(temp) == 0:
        temp.append('')
        temp[0] = ['', '']
    for item in temp[0]:
        items.append(item.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", ""))
    return items


def thread_process(startPage, endPagae, jobName):
    # 2秒超时，防止卡死
    timeout = 2
    socket.setdefaulttimeout(timeout)

    # 获取游标
    db = get_db_conn()
    cursor = db.cursor()
    tbName = '51Job抓取_' + jobName + '_北上广深杭_不限行业'

    for each in range(startPage, endPagae):
        index = (each - 1) * 50 + 1
        # 因为是分开存储excel，所以需要修正行数
        index = (index - (startPage - 1) * 50)
        # 二维数组：[0] => 职位 职位url 公司名 工作地点 薪资 发布时间
        temp = []
        try:
            temp = get(get_content(jobName, each))
        except Exception:
            print("error")
            continue
            
        for i in range(len(temp)):
            url = temp[i][1]
            print('%d %d %d%% %s' % (i, index, int(each * 100 / endPagae), url))
            # 初始化11空值
            descItems = []
            # 只抓取发布在51job上的职位描述
            if 'https://jobs.51job.com' in url:
                try:
                    descItems = get_job_desc(url)
                except Exception:
                    print("error")
                    continue
            else:
                continue

            # 拼接sql语句
            nowDate = datetime.datetime.now().strftime('%Y-%m-%d')  #现在
            # pymysql.escape_string：字符串转义
            sql = 'insert into `{0}` values("{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}",\
                "{9}","{10}","{11}","{12}","{13}","{14}","{15}","{16}","{17}","{18}")'\
                .format(tbName,temp[i][0],temp[i][1],temp[i][2],temp[i][3],temp[i][4],nowDate,temp[i][5],\
                descItems[3],descItems[0],descItems[1],descItems[2],descItems[4],descItems[5],descItems[6],\
                pymysql.escape_string(descItems[7]),pymysql.escape_string(descItems[8]),descItems[9],descItems[10])

            # 插入
            cursor.execute(sql)
            # 提交到数据库执行(一次提交10条)
            if i % 10 == 0 or i == (len(temp)-1):
                db.commit()
    # 关闭游标 和 数据链接
    cursor.close()
    db.close()

class myThread(threading.Thread):  # 自定义线程
    def __init__(self, name, startPage, endPage, jobName):
        threading.Thread.__init__(self)
        self.name = name
        self.startPage = startPage
        self.endPage = endPage
        self.jobName = jobName

    def run(self):
        print("start thread:" + self.name)
        thread_process(self.startPage, self.endPage, self.jobName)
        print("exit thread:" + self.name)


def get_db_conn():
    db = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='12345',
        db='crawler',
        charset='utf8')  # 打开数据库连接
    return db


def create_db_table(jobName):
    db = get_db_conn()

    cursor = db.cursor()  # 使用cursor()方法获取操作游标
    tbName = '51Job抓取_' + jobName + '_北上广深杭_不限行业'
    sql = 'show tables like \'' + tbName + '\''  # 定义要执行的SQL语句

    # 不存在就创建表
    cursor.execute(sql)
    if cursor.rowcount <= 0:
        sql = 'CREATE TABLE `' + tbName + '` (' \
            '`JobName` text COMMENT "招聘职位",' \
            '`JobURL` text COMMENT "职位URL",' \
            '`Company` text COMMENT "公司",' \
            '`Adress` text COMMENT "地址",' \
            '`Salary` text DEFAULT NULL COMMENT "薪资",' \
            '`Date` date DEFAULT NULL COMMENT "抓取时间",' \
            '`PublishDate` text DEFAULT NULL COMMENT "发布时间",' \
            '`AllJobUrl` text COMMENT "该公司所有职位URL",' \
            '`CompanyType` text DEFAULT NULL COMMENT "公司类型",' \
            '`CompanySize` text DEFAULT NULL COMMENT "公司规模",' \
            '`Industry` text DEFAULT NULL COMMENT "所在行业",' \
            '`Education` text DEFAULT NULL COMMENT "学历",' \
            '`Experience` text DEFAULT NULL COMMENT "经验要求",' \
            '`Number` text DEFAULT NULL COMMENT "人数",' \
            '`Welfare` text COMMENT "福利",' \
            '`JobDesc` text COMMENT "职位信息",' \
            '`JobLabel` text DEFAULT NULL COMMENT "职位标签",' \
            '`ContactAdress` text DEFAULT NULL COMMENT "联系地址"' \
            ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'
        cursor.execute(sql)
        print("已成功创建表：" + tbName)

    # 关闭游标 和 数据库链接
    cursor.close()
    db.close()


def start_write_to_mysql(jobName):
    # 确保表已创建
    create_db_table(jobName)

    # 条数解析
    total = get_total_count(get_content(jobName, 1))
    total = re.sub(r'\D', "", total)  # 提取数字
    totalPage = int((int(total) / 50)) + 1
    #totalPage = 10
    print('total:' + str(total) + ',totalPage:' + str(totalPage))

    # 启用线程抓取，假设CPU为4核，则启用8线程
    threads = []
    threadNum = 2
    threadPageSize = int(totalPage / threadNum)
    threadLastPageSize = threadPageSize + (totalPage % threadNum)
    for i in range(0, threadNum):
        startPage = i * threadPageSize
        endPage = startPage + threadPageSize
        # 处理除不尽的情况
        if (i + 1) == threadNum:
            endPage = (startPage + threadLastPageSize)
        thread = myThread("thread" + str(i), startPage, endPage, jobName)
        thread.start()
        threads.append(thread)

    # 等待所有线程抓取完毕
    for t in threads:
        t.join()

    print('successful and exit.')


if __name__ == '__main__':
    # 技术：java c# c/c++ html python php javascript android ios hadoop Node.js go
    # 领域：前端 后端 大数据 算法
    # 游戏：游戏 cocos2d U3D unity
    # 产品：产品经理 产品助理 项目经理 项目助理
    # 设计：视觉设计 UI设计 网页设计 平面设计 交互设计 用户研究
    # 新兴领域：人工智能 物联网 区块链 VR/AR 新能源
    # 高端岗位：技术经理 技术总监 架构师 CTO 运维总监 技术合伙人 项目总监 测试总监
    start_write_to_mysql("golang")
    start_write_to_mysql("ios")
    start_write_to_mysql("android")
    start_write_to_mysql("c++")
    start_write_to_mysql("java")
    start_write_to_mysql("html")
    start_write_to_mysql("python")
    start_write_to_mysql("php")
    start_write_to_mysql("javascript")
    start_write_to_mysql("hadoop")
    start_write_to_mysql("node.js")
    start_write_to_mysql("c#")

    start_write_to_mysql("前端")
    start_write_to_mysql("后端")
    start_write_to_mysql("大数据")
    start_write_to_mysql("算法")

    start_write_to_mysql("游戏")
    start_write_to_mysql("cocos2d")
    start_write_to_mysql("u3d")
    start_write_to_mysql("unity")
    
    start_write_to_mysql("产品经理")
    start_write_to_mysql("产品助理")
    start_write_to_mysql("项目经理")
    start_write_to_mysql("项目助理")
   
    start_write_to_mysql("视觉设计")
    start_write_to_mysql("UI设计")
    start_write_to_mysql("网页设计")
    start_write_to_mysql("平面设计")
    start_write_to_mysql("交互设计")
    start_write_to_mysql("用户研究")

    start_write_to_mysql("云计算")
    start_write_to_mysql("人工智能")
    start_write_to_mysql("物联网")
    start_write_to_mysql("区块链")
    start_write_to_mysql("VR/AR")
    start_write_to_mysql("新能源")
    start_write_to_mysql("自然语言处理")
    start_write_to_mysql("数据挖掘")
    start_write_to_mysql("数据采集")
    start_write_to_mysql("搜索算法")
    start_write_to_mysql("推荐算法")   

    start_write_to_mysql("机器学习")
    start_write_to_mysql("深度学习")
    start_write_to_mysql("图像算法")
    start_write_to_mysql("算法研究员")
    start_write_to_mysql("图像处理")
    start_write_to_mysql("图像识别")
    start_write_to_mysql("语音识别")
 
    start_write_to_mysql("技术经理")
    start_write_to_mysql("技术总监")
    start_write_to_mysql("部门经理")
    start_write_to_mysql("高级经理")
    start_write_to_mysql("研发经理")
    start_write_to_mysql("研发总监")
    start_write_to_mysql("高级总监")
    start_write_to_mysql("架构师")
    start_write_to_mysql("CTO")
    start_write_to_mysql("运维总监")
    start_write_to_mysql("技术合伙人")
    start_write_to_mysql("项目总监")
    start_write_to_mysql("测试总监")
    
    start_write_to_mysql("市场营销")
    start_write_to_mysql("广告")
    start_write_to_mysql("运营")
    start_write_to_mysql("英语翻译")
