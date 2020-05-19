# -*- coding: UTF-8 -*-

from flask import Flask,render_template,redirect,url_for,flash,session,jsonify, request, g, abort
from flask_script import Manager,Server
from flask_wtf import Form
from flask_bootstrap import Bootstrap
from wtforms import StringField,PasswordField,SubmitField,validators,IntegerField,DateTimeField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import json
import pymysql
import random
from datetime import date, datetime
from decimal import Decimal
from flask_cors import *

app = Flask(__name__)
manager = Manager(app)
manager.add_command("runserver", Server(use_debugger=True))
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = "123"
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:123456@116.196.90.212:3307/student'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
CORS(app, supports_credentials = True) # 解决跨域问题

class UsersRecommend:
    def __init__(self, uuid):
        self.uuid = uuid
        self.my_db = pymysql.connect(host='116.196.90.212', user='root', password='123456', database='student', port=3307)
        self.res_data = list(self.my_db.db_ais['friends'].find({'status': {'$in': [2, -1]}}, {'friend_id': 1, 'user_id': 1}))  # 查询所有用户好友关系表
        self.direct_f = self.get_friends(uuid)  # 用户好友
        if len(self.direct_f) > 50:  # 好友过多时取随机50个
            self.direct_f = random.sample(self.direct_f, 50)

    def recommend_f(self, pageno, pagesize):
        if len(self.direct_f) > 0:
            indirect_f = [{'indirect_id': x, 'relations': []} for x in self.direct_f]  # 间接好友初始化
            for x in self.res_data:  # 遍历res_data, 统计间接好友的好友列表
                if x['userId'] in self.direct_f and x['toUserId'] not in self.direct_f and x['toUserId'] != self.uuid:
                    indirect_f[self.direct_f.index(x['userId'])]['relations'].append(x['toUserId'])
            recommends, recommends_idx = [], []
            for x in indirect_f:
                if len(x['relations']) > 50:  # 跳过直接好友中好友过多的
                    continue
                for y in x['relations']:
                    if y not in recommends_idx:
                        recommends_idx.append(y)
                        recommends.append({'uid': y, 'num': 0, 'score': 0})
                    recommends[recommends_idx.index(y)]['score'] += 1  # 可惩罚‘过热’用户
                    recommends[recommends_idx.index(y)]['num'] += 1
            recommends.sort(key=lambda x: x['score'], reverse=True)  # 按共同好友数排序
            return [{'uid': x['uid'], 'common_friends': x['num']} for x in recommends][(pageno - 1) * pagesize:pageno * pagesize]  # 分页
        else:  # 用户尚未添加一个好友
            return []

    # 获取指定用户的好友列表
    def get_friends(self, usr_id):
        return [x['toUserId'] for x in self.res_data if x['userId'] == usr_id]

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)

    def default1(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class Interface:
    _fields = []
    _rela_fields = []

    def to_dict(self):
        result = {key: self.__getattribute__(key) for key in self._fields}
        for rf in self._rela_fields:
            result[rf] = []
            for item in self.__getattribute__(rf):
                result[rf].append(item.to_dict())
                # json.dumps(result[rf], ensure_ascii=False, cls=ComplexEncoder)
                # result[rf].json(item.to_dict(),cls=ComplexEncoder)
        return result

class Student(db.Model, Interface):
    __tablename__ = 'student'
    _fields = ['stu_account','stu_password','stu_name','stu_sex','stu_age','stu_phone','stu_weiXinName','stu_avatar','stu_weiXinNum','stu_courseNum','stu_cardDay','stu_interest','stu_position','longitude','latitude']
    _rela_fields = ['Record','Society']
    stu_account = db.Column(db.String,primary_key=True,nullable=False)
    stu_password = db.Column(db.String,nullable=False)
    stu_name = db.Column(db.String)
    stu_sex = db.Column(db.Enum('男','女'),default='男')
    stu_age = db.Column(db.Integer,default=18)
    stu_phone = db.Column(db.String)
    stu_weiXinName = db.Column(db.String)
    stu_avatar = db.Column(db.String)
    stu_weiXinNum = db.Column(db.String)
    stu_courseNum = db.Column(db.Integer,default=0)
    stu_cardDay = db.Column(db.Integer,default=0)
    stu_interest = db.Column(db.String)
    stu_position = db.Column(db.String,default='北京')
    longitude = db.Column(db.DECIMAL(10,7))
    latitude = db.Column(db.DECIMAL(10, 7))

    Record = db.relationship('Record', backref='student', lazy='dynamic')
    Society = db.relationship('Society', backref='student', lazy='dynamic')


class Course(db.Model, Interface):
    __tablename__ = 'course'
    _fields = ['course_id','course_name','course_notice','course_vf','course_studyNum','course_zanNum']
    _rela_fields = ['Stu_course']
    course_id = db.Column(db.Integer,primary_key=True,nullable=False)
    course_name = db.Column(db.String,nullable=False)
    course_notice = db.Column(db.String,nullable=False)
    course_vf = db.Column(db.String)
    course_studyNum = db.Column(db.Integer)
    course_zanNum = db.Column(db.Integer)
    Stu_course = db.relationship('Stu_course', backref='course',lazy='dynamic')

class Record(db.Model, Interface):
    __tablename__ = 'record'
    _fields = ['record_id','stu_account','record_time','record_content']
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True,nullable=False)
    stu_account = db.Column(db.String,db.ForeignKey(Student.stu_account),nullable=False)
    record_time = db.Column(db.DateTime,nullable=False)
    record_content = db.Column(db.String,nullable=False)

class Card(db.Model, Interface):
    __tablename__ = 'card'
    _fields = ['id','stu_account','card_time']
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,nullable=False)
    stu_account = db.Column(db.String,db.ForeignKey(Student.stu_account),nullable=False)
    card_time = db.Column(db.Date,nullable=False)

class Stu_course(db.Model, Interface):
    __tablename__ = 'stu_course'
    _fields = ['stu_course_id','stu_account','course_id']
    stu_course_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    stu_account = db.Column(db.String, db.ForeignKey(Student.stu_account), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey(Course.course_id),nullable=False)

class Society(db.Model, Interface):
    __tablename__ = 'society'
    _fields = ['society_id','user_id','friend_id','society_content','society_time']
    # _rela_fields = ['Student']
    society_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    friend_id = db.Column(db.String, db.ForeignKey(Student.stu_account),nullable=False)
    society_content = db.Column(db.String)
    society_time = db.Column(db.Date)

    # Student = db.relationship('Student', backref='society', lazy='dynamic')

class Chat(db.Model, Interface):
    __tablename__ = 'chat'
    _fields = ['chat_id','chat_type','user_id','friend_id','chat_content','chat_time']
    # _rela_fields = ['Student']
    chat_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    chat_type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    friend_id = db.Column(db.String, nullable=False)
    chat_content = db.Column(db.String)
    chat_time = db.Column(db.DateTime)

    # Student = db.relationship('Student', backref='society', lazy='dynamic')

# 后台管理
# class LoginForm(Form):
#     administrator_account = StringField("用户名: ",[validators.DataRequired(message="请输入有效的用户名"),])
#     administrator_password = PasswordField("密码: ",validators=[validators.DataRequired(),validators.Length(min=6,message="密码大于等于6位")])
#     submit = SubmitField("登录")

class Administrator(db.Model):
    __tablename__='administrator'
    administrator_account = db.Column(db.String,primary_key=True)
    administrator_password = db.Column(db.String)

# @app.route('/', methods=['GET','POST']) # 跳转到管理员登录页面
# def index():
#         return redirect(url_for('adminLogin'))

# @app.route('/adminLogin',methods=['GET','POST']) # 管理员登录页面
# def adminLogin():
#     myForm = LoginForm()
#     if myForm.validate_on_submit():
#         uname = myForm.administrator_account.data
#         pword = myForm.administrator_password.data
#         if len(Administrator.query.filter(and_(Administrator.administrator_account == uname,Administrator.administrator_password==pword)).all())>0:
#             session['is_login'] = True
#             return redirect(url_for('adminHome',u_name=uname))
#         else:
#             flash("用户名或密码不正确")
#             return redirect(url_for('adminLogin'))
#     return render_template('adminlogin.html',form=myForm)

# @app.route('/exitlogin') # 退出管理员登录页面
# def exit_login():
#     session['is_login']=False
#     return redirect(url_for('adminLogin'))

# @app.route('/<string:u_name>')# 管理员首页面
# def adminHome(u_name):
#     if session.get('is_login'):
#         administrator = Administrator.query.filter(Administrator.administrator_account==u_name).first()
#         return render_template("adminhome.html",administrator=administrator)
#     else:
#         return redirect(url_for('adminLogin'))

@app.route('/adminLogin', methods=['GET','POST']) # 管理员登录
def adminLogin():
    administrator_account = request.json.get('administrator_account')
    administrator_password = request.json.get('administrator_password')
    if administrator_account and administrator_password:
        administrator = Administrator.query.filter(Administrator.administrator_account == administrator_account, Administrator.administrator_password == administrator_password).first()
        if administrator:
            response = jsonify({'status': '1','administrator_account':administrator_account ,'role': '0'})
            # return ("1")
            return response
    response = jsonify({'status': '0'})
    # return ("0")
    return response

@app.route('/stuAdmin', methods=['GET','POST']) # 学员管理
def stuAdmin():
    stuAdmins = Student.query.all()
    return jsonify([stuAdmin.to_dict() for stuAdmin in stuAdmins])

@app.route('/courseAdmin', methods=['GET','POST']) # 课程管理 #学员-课程接口
def courseAdmin():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses])

@app.route('/cardAdmin', methods=['GET','POST']) # 打卡管理
def cardAdmin():
    records = Student.query.join(Record, Record.stu_account == Student.stu_account).filter(Record.stu_account == Student.stu_account).all()
    return jsonify([record.to_dict() for record in records])

@app.route('/addCourse', methods=['GET','POST']) # 管理员添加课程
def addCourse():
    course_id = request.json.get('course_id', None)
    course_name = request.json.get('course_name', None)
    course_notice = request.json.get('course_notice', None)
    course_vf = request.json.get('course_vf', None)
    new_course = Course (course_id=course_id, course_name=course_name, course_notice=course_notice, course_vf=course_vf)
    db.session.add(new_course)
    db.session.commit()
    response = jsonify({'status': '1'})
    response.status_code = 200
    return response

@app.route('/deleteCourse', methods=['GET','POST']) # 管理员删除课程
def deleteCourse():
    course_id = request.json.get('course_id', None)
    deletecourse = Course.query.filter(Course.course_id == course_id).first()
    db.session.delete(deletecourse)
    db.session.commit()
    response = jsonify({'status': '1'})
    response.status_code = 200
    return response


#前端
@app.route('/login', methods=['GET','POST']) # 登录
def login():
    stu_account = request.json.get('stu_account')
    stu_password = request.json.get('stu_password')
    if stu_account and stu_password:
        student = Student.query.filter(Student.stu_account == stu_account, Student.stu_password == stu_password).first()
        if student:
            return ("1")
            # return jsonify(student.to_dict())
    return ("0")

@app.route('/registered', methods=['GET','POST']) # 注册时判断用户是否存在
def registered():
    stu_account = request.json.get('stu_account')
    if len(Student.query.filter(Student.stu_account == stu_account).all()) > 0:
        return ("1")
    return ("0")

@app.route('/addStudent', methods=['GET','POST']) # 存入注册用户
def addStudent():
    stu_account = request.json.get('stu_account')
    stu_password = request.json.get('stu_password')
    new_student = Student(stu_account=stu_account, stu_password=stu_password)
    db.session.add(new_student)
    db.session.commit()
    return ("1")
    # response = jsonify({'status': '1'})
    # response.status_code = 200
    # return response

@app.route('/updateStudent', methods=['GET','POST']) # 存入注册用户个人信息
def updateStudent():
    stu_account = request.json.get('stu_account')
    stu_name = request.json.get('stu_name')
    stu_sex = request.json.get('stu_sex')
    stu_age = request.json.get('stu_age')
    stu_phone = request.json.get('stu_phone')
    stu_position = request.json.get('stu_position')
    stu_interest = request.json.get('stu_interest')
    updateStu = Student.query.filter(Student.stu_account == stu_account).first()
    updateStu.stu_name = stu_name
    updateStu.stu_sex = stu_sex
    updateStu.stu_age = stu_age
    updateStu.stu_phone = stu_phone
    updateStu.stu_position = stu_position
    updateStu.stu_interest = stu_interest
    db.session.commit()
    return ("1")

@app.route('/updatePass', methods=['GET','POST']) # 重置密码
def updatePass():
    stu_account = request.json.get('stu_account')
    stu_password = request.json.get('stu_password')
    updatePass = Student.query.filter(Student.stu_account == stu_account).first()
    updatePass.stu_password = stu_password
    db.session.commit()
    return ("1")

@app.route('/updatePosition', methods=['GET','POST']) # 更新位置信息（经纬度）
def updatePosition():
    stu_account = request.json.get('stu_account')
    longitude = request.json.get('longitude')
    latitude = request.json.get('latitude')
    updatePos = Student.query.filter(Student.stu_account == stu_account).first()
    updatePos.longitude = longitude
    updatePos.latitude = latitude
    db.session.commit()
    return ("1")

@app.route('/home', methods=['GET','POST']) # 首页  限制课程数 13条
def home():
    # courses = Course.query.limit(13)
    courses = Course.query.all()
    # courses = list(filter(lambda x: x.deleted == 0, courses))
    return jsonify([course.to_dict() for course in courses])


@app.route('/record', methods=['GET','POST']) # 打卡记录
def record():
    # records = Record.query.order_by(Record.record_time.desc()).all()
    # records = Record.query.limit(20)
    # courses = list(filter(lambda x: x.deleted == 0, courses))
    records = Student.query.join(Record, Record.stu_account == Student.stu_account).filter(Record.stu_account == Student.stu_account).order_by(-Record.record_time).all()
    return jsonify([record.to_dict() for record in records])
    # return json.dumps([record.to_dict() for record in records], ensure_ascii=False,cls=ComplexEncoder)

@app.route('/addRecord', methods=['GET','POST']) # 发布打卡记录
def addRecord():
    stu_account = request.json.get('stu_account', None)
    record_time = request.json.get('record_time', None)
    record_content = request.json.get('record_content', None)
    new_record = Record(stu_account=stu_account, record_time=record_time, record_content=record_content)
    db.session.add(new_record)
    db.session.commit()
    response = jsonify({'status': 'success'})
    response.status_code = 200
    return response

@app.route('/sort', methods=['GET','POST']) # 打卡排行
def sort():
    sorts = Student.query.order_by(-Student.stu_cardDay).all()
    return jsonify([sort.to_dict() for sort in sorts])

@app.route('/cardtime', methods=['GET','POST']) # 已签到的打卡日期
def cardtime():
    stu_account = request.json.get('stu_account')
    cardtimes = Card.query.filter(Card.stu_account == stu_account).all()
    return jsonify([cardtime.to_dict() for cardtime in cardtimes])

@app.route('/addcardtime', methods=['GET','POST']) # 添加学员打卡日期
def addcardtime():
    stu_account = request.json.get('stu_account')
    card_time = request.json.get('card_time')
    new_cardtime = Card(stu_account=stu_account, card_time=card_time)
    db.session.add(new_cardtime)
    db.session.commit()
    return ("1")

@app.route('/updatecardDay', methods=['GET','POST']) # 更新打卡天数
def updatecardDay():
    stu_account = request.json.get('stu_account')
    updatecardDay = Student.query.filter(Student.stu_account == stu_account).first()
    updatecardDay.stu_cardDay = updatecardDay.stu_cardDay + 1
    db.session.commit()
    return ("1")

@app.route('/mycourse', methods=['GET','POST']) # 我的课程、课程通知
def mycourse():
    stu_account = request.json.get('stu_account')
    mycourses = Course.query.join(Stu_course, Stu_course.course_id == Course.course_id).filter(Stu_course.stu_account == stu_account).all()
    return jsonify([mycourse.to_dict() for mycourse in mycourses])

@app.route('/addstu_course', methods=['GET','POST']) # 学员自己添加学习课程到我的课程列表，更新课程列表里的学习人数，我的课程数
def addstu_course():
    stu_account = request.json.get('stu_account')
    course_id = request.json.get('course_id')
    new_stu_course = Stu_course(stu_account=stu_account, course_id=course_id)
    db.session.add(new_stu_course)
    updateNum = Course.query.filter(Course.course_id == course_id).first()
    updateNum.course_studyNum = updateNum.course_studyNum + 1
    updateCourseNum = Student.query.filter(Student.stu_account == stu_account).first()
    updateCourseNum.stu_courseNum = updateCourseNum.stu_courseNum + 1
    db.session.commit()
    return ("1")

@app.route('/friendList', methods=['GET','POST']) # 好友列表
def friendList():
    user_id = request.json.get('stu_account')
    # friendLists = Society.query.join(Student,  Student.stu_account == user_id).filter(Student.stu_account == Society.friend_id).all()
    friendLists = Student.query.join(Society, Society.friend_id == Student.stu_account).filter(Society.user_id == user_id and Society.friend_id == Student.stu_account).all()
    return jsonify([friendList.to_dict() for friendList in friendLists])


@app.route('/firstrecommend', methods=['GET','POST']) # 获取好友列表
def firstrecommend():
    user_id = request.json.get('stu_account')
    friendLists = Society.query.filter(Society.user_id == user_id ).all()
    friendListA = jsonify([friendList.to_dict() for friendList in friendLists])
    return friendListA

@app.route('/recommend', methods=['GET','POST']) # 获取除了自己外的所有学员
def recommend():
    stu_account = request.json.get('stu_account')
    recommends = Student.query.filter(Student.stu_account != stu_account ).all()
    return jsonify([recommend.to_dict() for recommend in recommends])

@app.route('/addfriend', methods=['GET','POST']) # 学员自己添加好友
def addfriend():
    user_id = request.json.get('user_id')
    friend_id = request.json.get('friend_id')
    new_friend = Society(user_id=user_id, friend_id=friend_id)
    db.session.add(new_friend)
    new_friend1 = Society(user_id=friend_id, friend_id=user_id)
    db.session.add(new_friend1)
    db.session.commit()
    return ("1")

@app.route('/secondrecommend1', methods=['GET','POST']) # 获取兴趣，经纬度
def secondrecommend1():
    stu_account = request.json.get('stu_account')
    student = Student.query.filter(Student.stu_account == stu_account).first()
    return jsonify([student.to_dict()])

@app.route('/secondrecommend2', methods=['GET','POST']) # 获取与自己兴趣一致的学员
def secondrecommend2():
    stu_interest = request.json.get('stu_interest')
    stu_account = request.json.get('stu_account')
    friendinterests = Student.query.filter(Student.stu_interest == stu_interest , Student.stu_account != stu_account ).all()
    return jsonify([friendinterest.to_dict() for friendinterest in friendinterests])

@app.route('/chatcontent', methods=['GET','POST']) # 获取聊天消息
def chatcontent():
    user_id = request.json.get('user_id')
    friend_id = request.json.get('friend_id')
    chatcontents = Chat.query.filter(Chat.user_id == user_id, Chat.friend_id == friend_id,).order_by(-Chat.chat_time).all()
    return jsonify([chatcontent.to_dict() for chatcontent in chatcontents])

@app.route('/addchatcontent', methods=['GET','POST']) # 增加聊天消息
def addchatcontent():
    user_id = request.json.get('user_id')
    friend_id = request.json.get('friend_id')
    chat_type = request.json.get('chat_type')
    chat_content = request.json.get('chat_content')
    chat_time = request.json.get('chat_time')
    new_chatcontent = Chat(user_id=user_id, friend_id=friend_id, chat_type=chat_type, chat_content=chat_content,chat_time=chat_time)
    db.session.add(new_chatcontent)
    if (chat_type == 1):
        chat_type1 = 0
    else:
        chat_type1 = 1
    new_chatcontent1 = Chat(user_id=friend_id, friend_id=user_id, chat_type=chat_type1, chat_content=chat_content,chat_time=chat_time)
    db.session.add(new_chatcontent1)
    db.session.commit()
    return ("1")


if __name__ == '__main__':
    app.run()





