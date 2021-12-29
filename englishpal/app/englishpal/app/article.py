from WordFreq import WordFreq
from UseSqlite import InsertQuery, RecordQuery
import pickle_idea, pickle_idea2
import os
import random
from datetime import datetime
from flask import session
from difficulty import get_difficulty_level, text_difficulty_level, user_difficulty_level
#根目录
path_prefix = './' # comment this line in deployment

#获取文章总数
def total_number_of_essays():
    #创建查询类，写在UseSqlite.py中
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT * FROM article")
    rq.do()
    result = rq.get_results()
    return  len(result)


#读取文章历史
def load_freq_history(path):
    #os.path.exists(path) 如果路径 path 存在，返回 True；如果路径 path 不存在，返回 False。
    #pickle_idea中有pickle包，pickle模块实现了用于序列化和反序列化Python对象结构的二进制协议
    d = {}
    #检测文件是否存在
    if os.path.exists(path):
        #把文件读取出来，返回字典d
        d = pickle_idea.load_record(path)
    return d


#计算文章难度
def within_range(x, y, r):
    return x > y and abs(x - y) <= r


#获取文章的标题
def get_article_title(s):
    return s.split('\n')[0]

#获取文章的内容
def get_article_body(s):
    lst = s.split('\n')
    #移除第一行
    lst.pop(0)
    return '\n'.join(lst)


#获取今天的文章
def get_today_article(user_word_list, articleID):

    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    if articleID == None:
        rq.instructions("SELECT * FROM article")
    else:
        rq.instructions('SELECT * FROM article WHERE article_id=%d' % (articleID))
    rq.do()
    result = rq.get_results()
    #random.shuffle() 函数将序列中的元素随机打乱
    random.shuffle(result)

    #根据用户的英语水平来选择文章
    d1 = load_freq_history(path_prefix + 'static/frequency/frequency.p')
    #读取单词的等级
    d2 = load_freq_history(path_prefix + 'static/words_and_tests.p')
    #获得每个单词的等级
    d3 = get_difficulty_level(d1, d2)

    d = {}
    d_user = load_freq_history(user_word_list)
    #计算用户的英语水平
    user_level = user_difficulty_level(d_user, d3) # more consideration as user's behaviour is dynamic. Time factor should be considered.

    #计算文章难度
    random.shuffle(result) # shuffle list
    d = random.choice(result)
    text_level = text_difficulty_level(d['text'], d3)

    #从数据库中选择文章
    if articleID == None:
        for reading in result:
            text_level = text_difficulty_level(reading['text'], d3)
            #random.guass()返回具有高斯分布的随机浮点数
            factor = random.gauss(0.8, 0.1) # a number drawn from Gaussian distribution with a mean of 0.8 and a stand deviation of 1
            #选择文章
            if within_range(text_level, user_level, (8.0 - user_level)*factor):
                d = reading
                break


    article_title = get_article_title(d['text'])
    article_body = get_article_body(d['text'])
    article = {"user_level": user_level, "text_level": text_level, "data": d['date'], "article_title": article_title,
               "article_body": article_body, "soure": d['source'], "question": get_question_part(d['question']),
               "answer": get_answer_part(d['question'])}
    session['articleID'] = d['article_id']
    return article

#判断是否已经出现了该单词
def appears_in_test(word, d):
    if not word in d:
        return ''
    else:
        return ','.join(d[word])

#获取时间
def get_time():
    return datetime.now().strftime('%Y%m%d%H%M') # upper to minutes

#获取文章的问题
def get_question_part(s):
    s = s.strip()
    result = []
    flag = 0
    for line in s.split('\n'):
        line = line.strip()
        if line == 'QUESTION':
            result.append(line)
            flag = 1
        elif line == 'ANSWER':
            flag = 0
        elif flag == 1:
            result.append(line)
    return result

#获取文章题目的答案
def get_answer_part(s):
    s = s.strip()
    result = []
    flag = 0
    for line in s.split('\n'):
        line = line.strip()
        if line == 'ANSWER':
            flag = 1
        elif flag == 1:
            result.append(line)
    # https://css-tricks.com/snippets/javascript/showhide-element/

    result = "".join(result)
    return result