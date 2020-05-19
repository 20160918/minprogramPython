# # -*- coding: UTF-8 -*-
# from flask import Flask,request
# import pymysql
# import os
# import json
# from flask_cors import *
# os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
# from datetime import date, datetime
#
# app = Flask(__name__)
#
# class ComplexEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, datetime):
#             return obj.strftime('%Y-%m-%d %H:%M:%S')
#         elif isinstance(obj, date):
#             return obj.strftime('%Y-%m-%d')
#         else:
#             return json.JSONEncoder.default(self, obj)
#
# @app.route('/users', methods=["GET", "POST"])
# def users():
#     # 与数据库建立连接
#     connect_obj = pymysql.connect(host='116.196.90.212', user='root', password='123456', database='student', port=3307)
#     cur = connect_obj.cursor()  # 获取游标
#     sql = 'select * from student'
#     cur.execute(sql)
#     data = cur.fetchall()
#     # print(data)
#     text = {}
#     para = []
#     for i in data:
#         text = {'stu_account':i[0],'stu_password':i[1],'stu_name':i[2],'stu_sex':i[3],'stu_age':i[4],'stu_phone':i[5],'stu_weiXinName':i[6],'stu_avatar':i[7],'stu_weiXinNum':i[8],'stu_courseNum':i[9],'stu_cardDay':i[10],'stu_interest':i[11],'stu_position':i[12]}
#         # print(text)
#         para.append(text)
#     return json.dumps(para, ensure_ascii=False)
#
# @app.route('/record', methods=["GET", "POST"])
# def record():
#     # 与数据库建立连接
#     connect_obj = pymysql.connect(host='116.196.90.212', user='root', password='123456', database='student', port=3307)
#     cur = connect_obj.cursor()  # 获取游标
#     sql = 'select * from record'
#     cur.execute(sql)
#     data = cur.fetchall()
#     # print(data)
#     text1 = {}
#     para = []
#     for i in data:
#         text1 = {'record_id':i[0],'stu_account':i[1],'record_time':i[2],'record_content':i[3]}
#         # print(text)
#         para.append(text1)
#     return json.dumps(para, ensure_ascii=False,cls=ComplexEncoder)
#
# @app.route('/home', methods=["GET", "POST"])
# def home():
#     # 与数据库建立连接
#     connect_obj = pymysql.connect(host='116.196.90.212', user='root', password='123456', database='student', port=3307)
#     cur = connect_obj.cursor()  # 获取游标
#     sql = 'select * from course'
#     cur.execute(sql)
#     data = cur.fetchall()
#     # print(data)
#     text2 = {}
#     para = []
#     for i in data:
#         text2 = {'course_id':i[0],'course_name':i[1],'course_notice':i[2],'course_vf':i[3],'course_studyNum':i[4],'course_zanNum':i[5]}
#         # print(text)
#         para.append(text2)
#     return json.dumps(para, ensure_ascii=False)
#
# @app.route('/course', methods=["GET", "POST"])
# def course():
#     # qd_stu_account = request.values.get("stu_account")
#     # 与数据库建立连接
#     connect_obj = pymysql.connect(host='116.196.90.212', user='root', password='123456', database='student', port=3307)
#     cur = connect_obj.cursor()  # 获取游标
#     sql = "select * from stu_course"
#     cur.execute(sql)
#     data = cur.fetchall()
#     # print(data)
#     text3 = {}
#     para = []
#     for i in data:
#         text3 = {'stu_course_id':i[0],'stu_account':i[1],'course_id':i[2]}
#         # print(text)
#         para.append(text3)
#     return json.dumps(para, ensure_ascii=False)
#
# if __name__ == '__main__':
#     app.run()


# 与数据库建立连接
# connect_obj = pymysql.connect(host='116.196.90.212',user='root',password='123456',database='student',port=3307)
# cur = connect_obj.cursor()  # 获取游标

#  添加数据
# sql = "insert into students VALUES(%s,%s,%s,%s,%s)"
# count = cur.execute(sql,[0,'马冬梅',20,'男','880820'])  # 执行mysql语句
# connect_obj.commit()  # 数据修改时，一定要有这句话
# print('成功插入',count,'条数据')

#  删除数据
# sql = "DELETE FROM students WHERE id = 4 "
# count = cur.execute(sql)  # 执行mysql语句
# connect_obj.commit()  # 数据修改时，一定要有这句话
# print('成功删除',count,'条数据')

# 更新数据
# sql = "UPDATE students SET name = '李四' WHERE id = 3 "
# count = cur.execute(sql)  # 执行mysql语句
# connect_obj.commit()  # 数据修改时，一定要有这句话
# print('成功修改',count,'条数据')
#
# sql = 'select * from students'
# count = cur.execute(sql)  # 执行mysql语句
# print('共查出',count,'条数据')
# ret = cur.fetchall()  # 获取结果中的所有行
#
#
# #  cur.fetchmany(5)  # 获取结果中的下面5行
# #  cur.fetchone()  #  获取结果中的下一行
#
# for i in ret:
#     print(i)
#
# # 关闭连接
# cur.close()
# connect_obj.close()

from math import sin,radians,cos,asin,sqrt

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2]) #radians 角度转弧度
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) # 反正弦
    r = 6371
    haversine(113.0, 10.0, 114.0, 12.0)
    print(c * r)
    # return c * r


