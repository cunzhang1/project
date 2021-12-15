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
