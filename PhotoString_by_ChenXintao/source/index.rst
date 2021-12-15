**Lab 2**: Blueprint学习与使用
=================================================

**小组成员**

201932110118韩舒扬

201932110124李梁伟

201932110122黄士极

201932110121黄君杰


Abstract：
=================================================

Flask是一个轻量级的可定制框架，使用Python语言编写，较其他同类型框架更为灵活、轻便、安全且容易上手。它可以很好地结合MVC模式进行开发，开发人员分工合作，小型团队在短时间内就可以完成功能丰富的中小型网站或Web服务的实现。其中blueprint可以把不同功能的module分开，可以让应用模块化，针对大型应用
本实验主要来学习如何使用flask框架中的blueprint技术使提供了模块化管理程序路由的功能，使程序结构清晰、简单易懂，减少团队项目整合和各部分代码开发的操作难度和复杂性。


Introduction：
=================================================

在这个实验中，我们需要对 Photoprint 的项目结构进行分析，从源码以及功能来看，它是使用了flask框架实现了照片上传并命名的功能的web项目。根据实验要求我们需要使用blueprint实现该程序的模块化并且同时实现照片的上传、查询、信息展示等功能。
Blueprint的基本概念：在  Blueprint被注册到应用之后，所要执行的操作的集合。当分配请求时， Flask 会把  Blueprint和视图函数关联起来，并生成两个端点之前的 URL 。
可以用Blueprint来开关一些模块（功能）和宏定义类似，但不是可插拔的应用而是一套可以注册在应用中的操作，并且可以注册多次。或者简单滴需要降低耦合，提高模块复用率。比如开发环境和应用环境的不同，可以用Blueprint来切换环境。
需要注意的是Blueprint是一个容器，用于存储可以在向应用程序注册Blueprint之后调用的视图方法，Flask使用Blueprint组织url并处理请求。一个Blueprint并不是一个完整的应用，它不能独立于应用运行，而必须要注册到某一个应用中。
蓝图的运行机制：
蓝图是保存了一组将来可以在应用对象上执行的操作，注册路由就是一种操作
当在app对象上调用 route 装饰器注册路由时,这个操作将修改对象的url_map路由表
蓝图对象根本没有路由表，当我们在蓝图对象上调用route装饰器注册路由时,它只是在内部的一个延迟操作记录列表defered_functions中添加了一个项
当执行app对象的 register_blueprint() 方法时，应用对象将从蓝图对象的 defered_functions 列表中取出每一项，并以自身作为参数执行该匿名函数，即调用应用对象的 add_url_rule() 方法，这将真正的修改应用对象的usr_map路由表

Materials and Methods：
=================================================

PhotoString本身就应用了flask框架结构，我们第一步对该项目原有的功能代码进行分析，了解到了上传功能是如何实现的，从而选定该功能模块进行模块化转换。
 关于Blueprint的用法：如果使用errorhandler 修饰器，那么只有蓝本中的错误才能触发处理程序。即修饰器由蓝本提供。要想注册程序全局的错误处理程序，必须使用app_errorhandler。
，  创建 URL用法： 
Flask 会为蓝本中的全部端点加上一个命名空间，这样就可以在不同的蓝本中使用相同的端点名定义视图函数，而不会产生冲突。（跨蓝本）在单脚本程序中：index()视图函数的URL可使用url_for(‘index’) 
在蓝图中：index() 视图函数的URL 可使用 url_for(‘main.index’) 
另外，如果在一个蓝图的视图函数或者被渲染的模板中需要链接同一个蓝图中的其他端点，那么使用相对重定向，只使用一个点使用为前缀。简写形式（命名空间是当前请求所在的蓝本）：url_for(‘.index’)
如何使用蓝图可以通过下列四个步骤：
创建一个蓝图的包,例如users,并在__init__.py文件中创建蓝图对象
在这个蓝图目录下, 创建views.py文件,保存当前蓝图使用的视图函数
在users/init.py中引入views.py中所有的视图函数
在主应用main.py文件中的app对象上注册这个users蓝图对象


Results：
=================================================

Lab.py
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 15:42:51 2019

@author: Administrator
"""

from flask import Flask, request
from UseSqlite import InsertQuery
from datetime import datetime
from show import get_database_photos
from upload import upload_bp
from show import show_bp
from search import search_bp
from api_json import api_bp

app = Flask(__name__)

# 将蓝图注册到app
app.register_blueprint(upload_bp)
app.register_blueprint(show_bp)
app.register_blueprint(search_bp)
app.register_blueprint(api_bp)


@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        time_str = datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = time_str + '.jpg'
        uploaded_file.save('./static/upload/' + new_filename)
        time_info = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = request.form['description']
        path = './static/upload/' + new_filename
        iq = InsertQuery('./static/RiskDB.db')
        iq.instructions("INSERT INTO photo Values('%s','%s','%s','%s')" % (time_info, description, path, new_filename))
        iq.do()
        return '<p>You have uploaded %s.<br/> <a href="/">Return</a>.' % uploaded_file.filename
    else:
        page = '''
            <a href='/upload'>upload</a>
            <a href='/search'>search</a>
            <a href='/show'>show</a>
            <a href='/api_json'>api_json</a>
       '''
        page += get_database_photos()
        return page


if __name__ == '__main__':
    app.run(debug=True)

Upload.py
from flask import Blueprint

upload_bp = Blueprint('/upload', __name__)


@upload_bp.route('/upload')
def upload():   # 上传图片
    return '''<form action="/" method="post"enctype="multipart/form-data">
            <input type="file"name="file"><input name="description"><input type="submit"value="Upload"></form>'''


Search.py
from flask import Blueprint, request
from PIL import Image
from UseSqlite import RiskQuery

search_bp = Blueprint('/search', __name__)

def make_html_photo(s):  # 将数据库中获取到的图片格式化展现在网页上
    if s.strip() == '':
        return ''
    lst = s.split(',')
    picture_path = lst[2].strip()
    picture_name = lst[3].strip()
    im = Image.open(picture_path)
    im.thumbnail((400, 300))
    real_path = '.' + picture_path
    result = '<p>'
    result += '<i>%s</i><br/>' % (lst[0])
    result += '<i>%s</i><br/>' % (lst[1])
    result += '<a href="%s"><img src="../static/figure/%s"alt="风景图"></a>' % (real_path, picture_name)
    return result + '</p>'

def get_description_photos(description):  #从数据库中获取到所有图片的描述信息
    rq = RiskQuery('./static/RiskDB.db')
    rq.instructions("SELECT * FROM photo where description = '%s' " % description)
    rq.do()
    record = '<p>search result</p>'
    for r in rq.format_results().split('\n\n'):
        record += '%s' % (make_html_photo(r))
    return record + '</table>\n'

@search_bp.route('/search', methods=['POST', 'GET'])
def search():
    return '''<form action="/search/query-string"method="post"enctype="multipart/form-data">
                <input name="description"><input type="submit"value="search"></form>'''


@search_bp.route('/search/query-string', methods=['POST', 'GET'])
def query_string():
    if request.method == 'POST':
        description = request.form['description']
        page = get_description_photos(description)

    return page

Show.py
from flask import Blueprint
from PIL import Image
from UseSqlite import RiskQuery

show_bp = Blueprint('show', __name__)


def make_html_paragraph(s):  # 将数据库中获取到的图片和信息格式化展现在网页上
    if s.strip() == '':
        return ''
    lst = s.split(',')
    picture_path = lst[2].strip()
    picture_name = lst[3].strip()
    im = Image.open(picture_path)
    im.thumbnail((400, 300))
    im.save('./static/figure/' + picture_name, 'jpeg')
    result = '<p>'
    result += '<i>%s</i><br/>' % (lst[0])
    result += '<i>%s</i><br/>' % (lst[1])
    result += '<a href="%s"><img src="./static/figure/%s"alt="风景图"></a>' % (picture_path, picture_name)
    return result + '</p>'

def get_database_photos():  # 从数据库中获取到所有图片和描述信息
    rq = RiskQuery('./static/RiskDB.db')
    rq.instructions("SELECT * FROM photo ORDER By time desc")
    rq.do()
    record = '<p>My past photo</p>'
    for r in rq.format_results().split('\n\n'):  # 将每条图片信息记录按照一定的样式显示在网页上
        record += '%s' % (make_html_paragraph(r))
    return record + '</table>\n'

@show_bp.route('/show')  # 展示所有照片信息页面
def show():
    return get_database_photos()

Api_json.py
import json
import os.path

from flask import Blueprint
from UseSqlite import RiskQuery

api_bp = Blueprint('/api_json', __name__)

@api_bp.route('/api_json', methods=['POST', 'GET'])
def api_json():  # 获取所有图片信息
    rq = RiskQuery('./static/RiskDB.db')
    rq.instructions("SELECT * FROM photo ORDER By time desc")
    rq.do()
    lst = []  # 存储输出的图片信息的数组
    page = "图片信息：" + '<p>'
    i = 1  # 图片是的序号
    for r in rq.format_results().split('\n\n'):
        photo = r.split(',')
        if photo[0] != '':
            picture_time = photo[0]  # 获取图片的上传时间
            picture_description = photo[1]  # 获取图片的描述
            picture_path = photo[2].strip()  # 获取图片的存储路径
            photo_size = str(format((os.path.getsize(picture_path) / 1024), '.2f')) + 'KB'  # 获取图片的文件大小，单位为KB
            lst = [{'ID': i, 'upload_date': picture_time, 'description': picture_description, 'photo_size': photo_size}]  # 将图片信息存储到lst信息中
            lst2 = json.dumps(lst[0], sort_keys=True, indent=4, separators=(',', ':'))  # 转换成json对象
            page +="图片%d: " '%s' %(i,lst2) +'<p>'  # 在网页中输出图片信息
            i += 1
        else:
            page += "无图片"
    return page

Usesqlite.py
# Reference: Dusty Phillips.  Python 3 Objected-oriented Programming Second Edition. Pages 326-328.
# Copyright (C) 2019 Hui Lan

import sqlite3

class Sqlite3Template:
    def __init__(self, db_fname):
        self.db_fname = db_fname
        
    def connect(self, db_fname):
        self.conn = sqlite3.connect(self.db_fname)
    
    def instructions(self, query_statement):
        raise NotImplementedError()
    
    def operate(self):
        self.results = self.conn.execute(self.query) # self.query is to be given in the child classes
        self.conn.commit()
        
    def format_results(self):
        raise NotImplementedError()  
    
    def do(self):
        self.connect(self.db_fname)
        self.instructions(self.query)
        self.operate()
        
        
class InsertQuery(Sqlite3Template):
    def instructions(self, query):
        self.query = query
        

class RiskQuery(Sqlite3Template):
    def instructions(self, query):
        self.query = query

    def format_results(self):
        output = []
        for row in self.results.fetchall():
            output.append(', '.join([str(i) for i in row]))
        return '\n\n'.join(output)    


if __name__ == '__main__':
    
    #iq = InsertQuery('RiskDB.db')
    #iq.instructions("INSERT INTO inspection Values ('FoodSupplies', 'RI2019051301', '2019-05-13', '{}')")
    #iq.do()
    #iq.instructions("INSERT INTO inspection Values ('CarSupplies', 'RI2019051302', '2019-05-13', '{[{\"risk_name\":\"elevator\"}]}')")
    #iq.do()
    
    rq = RiskQuery('RiskDB.db')
    rq.instructions("SELECT * FROM inspection WHERE inspection_serial_number LIKE 'RI20190513%'")
    rq.do()
    print(rq.format_results())

Discussions：
=================================================

PhotoString使用了Flask框架，使用者可以查看到所有上传图片、上传并命名图片、查找图片、了解上传图片的信息。
但是，原来的PhotoString只能完成上传图片的目标，我们则通过相关知识的了解和学习对源码进行了模块化设计，并且添加了许多功能。源码缺点在于flask框架在大型项目开发时若没有进行blueprint处理，可能导致开发过程遇到需要修改的部分会增加开发难度，需要对整体代码进行修改调整测试，而模块化处理可以将项目的功能分为小部分进行调整调用。
这个实验的主要目的就是体验blueprint等工具的使用,让我们可以了解一个项目如何进行模块化,并且对这个项目有一个全面的理解。同时这也让我们明白大型项目进行团队开发时不同部分的分组式开发需要通过该工具使程序结构清晰、简单易懂，减少团队项目整合和各部分代码开发的操作难度和复杂性。运用好blueprint，我们可以很好地分析出分清楚各个模块的作用与相互之间的依赖关系。
因此，通过blueprint的使用，对我们未来进行团队开发任务有所帮助。


Resources：
=================================================
[1]Flask-蓝图【J/OL】. https://www.jianshu.com/p/7c474ee9ffee 【引用日期：2021年12月15日】
[2]Blueprint（蓝本/蓝图）学习笔记【J/OL】. https://segmentfault.com/a/1190000011000629【引用日期：2021年12月15日】


