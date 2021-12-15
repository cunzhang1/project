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
    page = ''
    i = 1  # 图片是的序号
    for r in rq.format_results().split('\n\n'):
        photo = r.split(',')
        picture_time = photo[0]  # 获取图片的上传时间
        picture_description = photo[1]  # 获取图片的描述
        picture_path = photo[2].strip()  # 获取图片的存储路径
        photo_size = str(format((os.path.getsize(picture_path) / 1024), '.2f')) + 'KB'  # 获取图片的文件大小，单位为KB
        lst = [{'ID': i, 'upload_date': picture_time, 'description': picture_description, 'photo_size': photo_size}]  # 将图片信息存储到lst信息中
        lst2 = json.dumps(lst[0], sort_keys=True, indent=4, separators=(',', ':'))  # 转换成json对象
        page +="图片%d: " '%s' %(i,lst2) +'<p>'  # 在网页中输出图片信息
        i += 1
    return page
