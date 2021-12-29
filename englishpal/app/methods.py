from WordFreq import WordFreq
from UseSqlite import InsertQuery, RecordQuery
import os
import random
from datetime import datetime
#根目录
path_prefix = './' # comment this line in deployment

#随机获得广告词
def get_random_ads():
    #广告词选项
    ads = random.choice(['个性化分析精准提升', '你的专有单词本', '智能捕捉阅读弱点，针对性提高你的阅读水平'])
    return ads


#验证用户
def verify_user(username, password):
    #创建查询类，写在UseSqlite.py中
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions_with_parameters("SELECT * FROM user WHERE name=? AND password=?", (username, password))
    #方法名，带参执行的意思
    rq.do_with_parameters()
    result = rq.get_results()
    return result != []


#添加用户
def add_user(username, password):
    start_date = datetime.now().strftime('%Y%m%d')
    expiry_date = '20211230'
    rq = InsertQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("INSERT INTO user Values ('%s', '%s', '%s', '%s')" % (username, password, start_date, expiry_date))
    rq.do()


#检验用户名称是否可用
def check_username_availability(username):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT * FROM user WHERE name='%s'" % (username))
    rq.do()
    result = rq.get_results()
    return  result == []


#获取到期时间
def get_expiry_date(username):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT expiry_date FROM user WHERE name='%s'" % (username))
    rq.do()
    result = rq.get_results()
    if len(result) > 0:
        #返回到期时间
        return  result[0]['expiry_date']
    else:
        return '20191024'