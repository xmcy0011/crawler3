# -*- coding:utf-8 -*-
import socket
import urllib.request
import re
import xlwt  # 用来创建excel文档并写入数据
import pymysql
import threading  # 多线程抓取
import time
from urllib.parse import quote


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
    url = url_config(jobName) + str(page)+'.html'
    a = urllib.request.urlopen(url)  # 打开网址
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
    reg = re.compile(r'class="t1 ">.*? <a target="_blank" title="(.*?)" href="(.*?)".*? <span class="t2"><a target="_blank" title="(.*?)".*?<span class="t3">(.*?)</span>.*?<span class="t4">(.*?)</span>.*? <span class="t5">(.*?)</span>', re.S)  # 匹配换行符
    items = re.findall(reg, html)
    return items


def get_job_desc(url):  # 获取职位描述
    # url = "https://jobs.51job.com/shanghai/102581378.html?s=01&t=0"
    # if url == 'https://jobs.51job.com/shanghai/102581378.html?s=01&t=0':
    #     print('yes')
    a = urllib.request.urlopen(url)  # 打开网址
    html = a.read().decode('gbk')  # 读取源代码并转为unicode
    items = []

    # 该公司所有职位URL 公司类型 公司规模 公司行业
    reg = re.compile(r'<div class="cn">.*?<a track-type="jobsButtonClick" event-type="2" class="i_house" href="(.*?)" target="_blank">该公司所有职位</a>.*?<p class="msg ltype">(.*?)&nbsp;&nbsp;\|&nbsp;&nbsp;(.*?)&nbsp;&nbsp;\|&nbsp;&nbsp;(.*?)</p>', re.S)
    temp = re.findall(reg, html)
    if len(temp) == 0:
        temp.append('')
        temp[0] = ['', '', '', '']
    for item in temp[0]:
        items.append(item.replace("\r", "").replace(
            "\n", "").replace("\t", "").replace(" ", ""))

    # 学历（可为空）
    reg = re.compile(
        r'<em class="i2"></em>(.*?)</span>', re.S)
    temp = re.findall(reg, html)
    if len(temp) > 0:
        items.append(temp[0].replace("\r", "").replace(
            "\n", "").replace("\t", "").replace(" ", ""))
    else:
        items.append("")

    # 经验 招聘人数
    reg = re.compile(
        r'<div class="tCompany_main" >.*?<em class="i1"></em>(.*?)</span>.*?<em class="i3"></em>(.*?)</span>', re.S)
    temp = re.findall(reg, html)[0]
    for item in temp:
        items.append(item.replace("\r", "").replace(
            "\n", "").replace("\t", "").replace(" ", ""))

    # 福利标签（可为空）
    reg = re.compile(
        r'<div class="tCompany_main" >.*?<p class="t2">(.*?)</p>', re.S)
    temp = re.findall(reg, html)
    if len(temp) > 0:
        items.append(temp[0].replace("\r", "").replace(
            "\n", "").replace("\t", "").replace(" ", ""))
    else:
        items.append("")

    # 职位描述
    reg = re.compile(
        r'<div class="bmsg job_msg inbox">(.*?)<div class="mt10">', re.S)
    temp = re.findall(reg, html)[0]
    items.append(temp.replace("\r", "").replace(
        "\n", "").replace("\t", "").replace(" ", ""))

    # 职能类别
    reg = re.compile(
        r'<div class="mt10">.*?<p class="fp">.*?<span class="label">职能类别：</span>(.*?)</p>.*?</div>.*?<div class="share">', re.S)
    temp = re.findall(reg, html)[0]
    items.append(temp.replace("\r", "").replace(
        "\n", "").replace("\t", "").replace(" ", "").replace(r'<spanclass="el">', "").replace("</span>", " "))

    # 公司地址 公司信息
    reg = re.compile(
        r'<p class="fp">.*?<span class="label">上班地址：</span>(.*?)</p>.*?<div class="tmsg inbox">(.*?)</div>', re.S)
    temp = re.findall(reg, html)
    if len(temp) == 0:
        temp.append('')
        temp[0] = ['', '']
    for item in temp[0]:
        items.append(item.replace("\r", "").replace(
            "\n", "").replace("\t", "").replace(" ", ""))
    return items


def excel_write(items, index, ws):
    # 爬取到的内容写入excel表格
    for item in items:  # 职位信息
        for i in range(0, len(item)-1):
            ws.write(index, i, item[i])  # 行，列，数据
        index += 1


def thread_process(startPage, endPagae, jobName):
    # 2秒超时，防止卡死
    timeout = 2
    socket.setdefaulttimeout(timeout)

    datetime = time.strftime("%Y%m%d", time.localtime())
    newTable = "51Job抓取_%s_%s_北上广深杭_不限行业_%d.xls" % (
        datetime, jobName, startPage)  # 表格名称
    wb = xlwt.Workbook(encoding='utf-8')  # 创建excel文件，声明编码
    ws = wb.add_sheet('sheet1', cell_overwrite_ok=True)  # 创建表格
    headData = ['JobName', 'JobURL', 'Company', 'Adress', 'Salary', 'Date', 'AllJobUrl', 'CompanyType',
                'CompanySize', 'Industry', 'Education', 'Experience', 'Number', 'Welfare', 'JobDesc', 'JobLabel', 'ContactAdress']  # 表头部信息
    for colnum in range(0, len(headData)):
        ws.write(0, colnum, headData[colnum],
                 xlwt.easyxf('font: bold on'))  # 行，列

    for each in range(startPage, endPagae):
        index = (each-1)*50+1
        # 因为是分开存储excel，所以需要修正行数
        index = (index-(startPage-1)*50)
        # 职位 职位url 公司名 工作地点 薪资 发布时间
        temp = []
        try:
            temp = get(get_content(jobName, each))
        except:
            print("error")
            continue
        items = [[] for i in range(len(temp))]
        for i in range(len(temp)):
            url = temp[i][1]
            print('%d %d %d%% %s' % (i, index, int(each*100/endPagae), url))
            descItems = []
            # 只抓取发布在51job上的职位描述
            if 'https://jobs.51job.com' in url:
                try:
                    descItems = get_job_desc(url)
                except:
                    print("error")
            tempArr = []
            tempArr.extend(temp[i])
            tempArr.extend(descItems)
            items[i].extend(tempArr)
            # 每30个存一次，防止内存溢出
            # 平均500字，excel缓存不能超过32767个，发现特点职位描述，直接将缓存写到文件
            #jobDescLen = 0 if len(descItems) < 8 else len(descItems[8])
            #if i % 30 == 0 or (i+1) == len(temp) or jobDescLen > 1500:
            excel_write(items, index, ws)
        wb.save(newTable)
    wb.save(newTable)


class myThread (threading.Thread):  # 自定义线程
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


def start_write_to_excel(jobName):
    # 条数解析
    total = get_total_count(get_content(jobName, 1))
    total = re.sub(r'\D', "", total)  # 提取数字
    totalPage = int((int(total) / 50))+1
    # totalPage = 240
    print('total:'+str(total)+',totalPage:'+str(totalPage))

    # 启用线程抓取，假设CPU为4核，则启用8线程
    threads = []
    threadNum = 4
    threadPageSize = int(totalPage / threadNum)
    threadLastPageSize = threadPageSize + (totalPage % threadNum)
    for i in range(0, threadNum):
        startPage = i*threadPageSize
        endPage = startPage+threadPageSize
        # 处理除不尽的情况
        if (i + 1) == threadNum:
            endPage = (startPage + threadLastPageSize)
        thread = myThread("thread"+str(i), startPage, endPage, jobName)
        thread.start()
        threads.append(thread)

    # 等待所有线程抓取完毕
    for t in threads:
        t.join()

    print('successful and exit.')

# def create_db_table():
    # 使用 execute() 方法执行 SQL，如果表存在则删除


# def start_write_to_mysql():
#     # 打开数据库连接
#     db = pymysql.connect("localhost", "testuser", "test123", "TESTDB")
#     # 使用cursor()方法获取操作游标
#     cursor = db.cursor()
#     sql = 'insert into database test;'      # 定义要执行的SQL语句
#     for each in range(1, 2000):
#         index = (each-1)*50+1
#         # 职位 职位url 公司名 工作地点 薪资 发布时间
#         temp = get(get_content(each))
#         for i in range(len(temp)):
#             url = temp[i][1]
#             print(url)
#             # '该公司所有职位URL', '公司类型','公司规模', '所在行业', '学历', '经验要求', '人数', '福利', '职位信息', '职位标签', '联系地址'
#             descItems = []
#             # 只抓取发布在51job上的职位描述
#             if 'https://jobs.51job.com' in url:
#                 try:
#                     descItems = get_job_desc(url)
#                 except:
#                     print("error")

#     sql = 'drop database test;'      # 定义要执行的SQL语句


if __name__ == '__main__':
    # 技术：java c# c/c++ html python php javascript android ios 大数据 Node.js
    # 游戏：游戏 cocos2d U3D unity
    # 产品：产品经理 产品助理 项目经理 项目助理
    # 设计：视觉设计 UI设计 网页设计 平面设计 交互设计 用户研究
    # 新兴领域：人工智能 物联网 区块链 VR/AR 新能源
    # 高端岗位：技术经理 技术总监 架构师 CTO 运维总监 技术合伙人 项目总监 测试总监
    start_write_to_excel("产品经理")
    # thread_process(806, 961)
    # start_write_to_mysql()
