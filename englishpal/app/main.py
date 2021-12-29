#! /usr/bin/python3
# -*- coding: utf-8 -*-

###########################################################################
# Copyright 2019 (C) Hui Lan <hui.lan@cantab.net>
# Written permission must be obtained from the author for commercial uses.
###########################################################################

from WordFreq import WordFreq
from wordfreqCMD import youdao_link, sort_in_descending_order
from UseSqlite import InsertQuery, RecordQuery
import pickle_idea, pickle_idea2
import os
import random, glob
from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, session, abort, flash, get_flashed_messages
from difficulty import get_difficulty_level, text_difficulty_level, user_difficulty_level
from methods import get_random_ads, verify_user, add_user, check_username_availability, get_expiry_date
from article import total_number_of_essays, load_freq_history, within_range, get_article_title, get_article_body, get_today_article, appears_in_test, get_time, get_question_part, get_answer_part

#获取flask对象
app = Flask(__name__)
#设置关键秘钥
app.secret_key = 'lunch.time!'
#根目录
path_prefix = './' # comment this line in deployment


#重置用户
@app.route("/<username>/reset", methods=['GET', 'POST'])
def user_reset(username):
    if request.method == 'GET':
        session['articleID'] = None
        #url_for()函数是用于构建指定函数的URL，而且url_for操作对象是函数，而不是route里的路径。
        return redirect(url_for('userpage', username=username))
    else:
        return 'Under construction'


@app.route("/mark", methods=['GET', 'POST'])
def mark_word():
    if request.method == 'POST':
        d = load_freq_history(path_prefix + 'static/frequency/frequency.p')
        lst_history = pickle_idea.dict2lst(d)
        lst = []
        for word in request.form.getlist('marked'):
            lst.append((word, 1))
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, path_prefix + 'static/frequency/frequency.p')
        return redirect(url_for('mainpage'))
    else:
        return 'Under construction'


@app.route("/", methods=['GET', 'POST'])
def mainpage():
    #用POST方法获取主页 mainpage_post.html
    if request.method == 'POST':  # when we submit a form
        content = request.form['content']
        f = WordFreq(content)
        lst = f.get_freq()

        # save history 
        d = load_freq_history(path_prefix + 'static/frequency/frequency.p')
        lst_history = pickle_idea.dict2lst(d)
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, path_prefix + 'static/frequency/frequency.p')

        return render_template("mainpage_post.html",lst = lst)
    #用GET方法获取主页 mainpage_get.html
    elif request.method == 'GET': # when we load a html page

        #获取过去的记录？
        d = load_freq_history(path_prefix + 'static/frequency/frequency.p')
        des_ord = sort_in_descending_order(pickle_idea.dict2lst(d))
        #把需要的内容都保存到一个列表中，youdao_link(x[0])，x[0]，x[1]
        you_list = []
        for x in des_ord:
            if x[1] <= 99:
                break
            you_list.append({"link":youdao_link(x[0]),"x":x[0],"y":x[1]})
        #文章总数
        num = total_number_of_essays()
        #添加随机广告语
        ads = get_random_ads()
        lend = len(d)
        #返回到前端 mainpage_get.html
        return render_template("mainpage_get.html",
                               d = d,
                               ads = ads,
                               num = num,
                               you_list = you_list,
                               lend = lend)


@app.route("/<username>/mark", methods=['GET', 'POST'])
def user_mark_word(username):
    username = session[username]
    user_freq_record = path_prefix + 'static/frequency/' +  'frequency_%s.pickle' % (username)
    if request.method == 'POST':
        d = load_freq_history(user_freq_record)
        lst_history = pickle_idea2.dict2lst(d)
        lst = []
        for word in request.form.getlist('marked'):
            lst.append((word, [get_time()]))
        d = pickle_idea2.merge_frequency(lst, lst_history)
        pickle_idea2.save_frequency_to_pickle(d, user_freq_record)
        return redirect(url_for('userpage', username=username))
    else:
        return 'Under construction'

#生词库单词 当点击不熟悉的选项时调用
@app.route("/<username>/<word>/unfamiliar", methods=['GET', 'POST'])
def unfamiliar(username,word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea.unfamiliar(user_freq_record,word)
    session['thisWord'] = word  # 1. put a word into session
    session['time'] = 1
    return redirect(url_for('userpage', username=username))


#生词库单词 当点击熟悉的选项时调用
@app.route("/<username>/<word>/familiar", methods=['GET', 'POST'])
def familiar(username,word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea.familiar(user_freq_record,word)
    session['thisWord'] = word  # 1. put a word into session
    session['time'] = 1
    return redirect(url_for('userpage', username=username))


#生词库单词 当点击删除的选项时调用
@app.route("/<username>/<word>/del", methods=['GET', 'POST'])
def deleteword(username,word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea2.deleteRecord(user_freq_record,word)
    flash(f'<strong>{word}</strong> is no longer in your word list.')
    return redirect(url_for('userpage', username=username))

#用户主页
@app.route("/<username>", methods=['GET', 'POST'])
def userpage(username):

    #检查是否已经登录 login_first.html
    if not session.get('logged_in'):
        return render_template("login_first.html")

    #检查用户是否过期 over_expiry.html
    user_expiry_date = session.get('expiry_date')
    if datetime.now().strftime('%Y%m%d') > user_expiry_date:
        return render_template("over_expiry.html",username = username)

    
    username = session.get('username')

    user_freq_record = path_prefix + 'static/frequency/' +  'frequency_%s.pickle' % (username)

    #显示已经选取的生词 check_unknow_post.html
    if request.method == 'POST':  # when we submit a form
        content = request.form['content']
        f = WordFreq(content)
        lst = f.get_freq()

        count = 1
        words_tests_dict = pickle_idea.load_record(path_prefix + 'static/words_and_tests.p')
        you_list=[]
        for x in lst:

            you_list.append(
                {"count": count, "link": youdao_link(x[0]), "appear": appears_in_test(x[0], words_tests_dict),
                 "x0": x[0], "x1": x[1]})
            count += 1

        return render_template("check_unknow_post.html", you_list = you_list,username = username)
    #生词库中不存在单词时 check_unknow_get.html
    elif request.method == 'GET': # when we load a html page
        d = load_freq_history(user_freq_record)

        des_ord = []
        if len(d) > 0:
            lst = pickle_idea2.dict2lst(d)
            lst2 = []
            for t in lst:
                lst2.append((t[0], len(t[1])))

            #创建一个用来传值的容器
            count = 0
            for x in sort_in_descending_order(lst2):
                des_ord.append({"sessioncheck":True,"wlist":True,"you_link":None,"word":None,"jword":None,"freq":None,"username":None})
                word = x[0]
                freq = x[1]
                #用sessioncheck来保存信息
                if session.get('thisWord') == x[0] and session.get('time') == 1:
                    session['time'] = 0   # discard anchor
                else:
                    des_ord[count]["sessioncheck"] = False

                #用wlist来保存信息
                if isinstance(d[word], list): # d[word] is a list of dates
                    des_ord[count]["you_link"] = youdao_link(word)
                    des_ord[count]["word"] = word
                    des_ord[count]["jword"] = '; '.join(d[word])
                    des_ord[count]["freq"] = freq
                    des_ord[count]["username"] = username
                elif isinstance(d[word], int): # d[word] is a frequency. to migrate from old format.
                    des_ord[count]["wlist"] = False
                    des_ord[count]["you_link"] = youdao_link(word)
                    des_ord[count]["word"] = word
                    des_ord[count]["freq"] = freq

                count +=1

        return render_template("check_unknow_get.html",
                               lend = len(d),
                               username = username,
                               article = get_today_article(user_freq_record, session['articleID']),
                               des_ord = des_ord
                               )

### Sign-up, login, logout ###
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        available = check_username_availability(username)
        if not available:
            flash('用户名 %s 已经被注册。' % (username))
            return render_template('signup.html')
        elif len(password.strip()) < 4:
            return '密码过于简单。'
        else:
            add_user(username, password)
            verified = verify_user(username, password)
            if verified:
                session['logged_in'] = True
                session[username] = username
                session['username'] = username
                session['expiry_date'] = get_expiry_date(username)
                session['articleID'] = None
                return render_template("congratulations_registration.html", username = username)
            else:
                return "用户名密码验证失败。"


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
            return render_template('login.html')
        if not session.get('logged_in'):
        else:
            return '你已登录 <a href="/%s">%s</a>。 登出点击<a href="/logout">这里</a>。' % (session['username'], session['username'])
    elif request.method == 'POST':
        # check database and verify user
        username = request.form['username']
        password = request.form['password']
        verified = verify_user(username, password)
        if verified:
            session['logged_in'] = True
            session[username] = username
            session['username'] = username
            user_expiry_date = get_expiry_date(username)
            session['expiry_date'] = user_expiry_date
            session['articleID'] = None
            return redirect(url_for('userpage', username=username))
        else:
            return '无法通过验证。'


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('mainpage'))


if __name__ == '__main__':
    #app.secret_key = os.urandom(16)
    #app.run(debug=False, port='6000')
    app.run(debug=True)        
    #app.run(debug=True, port='6000')
    #app.run(host='0.0.0.0', debug=True, port='6000')
