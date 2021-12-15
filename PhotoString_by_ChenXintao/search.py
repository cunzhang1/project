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
