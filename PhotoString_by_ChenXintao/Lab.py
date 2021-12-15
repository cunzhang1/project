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
