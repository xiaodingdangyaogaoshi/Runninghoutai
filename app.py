import json
import os
import random
import time

import MySQLdb
import requests
from flask.json import jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, fresh_login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, current_app, render_template, request
from selenium.webdriver.common import alert
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import *
import config
import pymysql
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, redirect, url_for, flash, abort
#from flask.ext.login import (LoginManager, UserMixin, login_user, logout_user,
                            #current_user, login_required, fresh_login_required)
app = Flask(__name__)
bootstrap=Bootstrap(app)
basedir = os.path.abspath(os.path.dirname(__file__))
login_manager = LoginManager(app)
# 设置登录视图的名称，如果一个未登录用户请求一个只有登录用户才能访问的视图，
# 则闪现一条错误消息，并重定向到这里设置的登录视图。
# 如果未设置登录视图，则直接返回401错误。
login_manager.login_view = 'login'
# 设置当未登录用户请求一个只有登录用户才能访问的视图时，闪现的错误消息的内容，
# 默认的错误消息是：Please log in to access this page.。
login_manager.login_message = 'Unauthorized User'
# 设置闪现的错误消息的类别
login_manager.login_message_category = "info"

users = [
    {'username': 'root', 'password': '123'},
    {'username': 'ting', 'password': '123'}
]

app.config.from_object(config)
db=SQLAlchemy(app)

class runningdata(db.Model):
    __tablename__='runningdata'

    id = db.Column(db.Integer, nullable=False)
    la=db.Column(db.Float,nullable=False)
    long = db.Column(db.Float, nullable=False)
    userid=db.Column(db.Integer,nullable=False,primary_key=True)
    tag=db.Column(db.Integer,nullable=False)
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
db.create_all()

class Du:
    def keys(self):
        return ('latitude','longtitude')
    def __getitem__(self, item):
        return
@app.route('/system')
@login_required
def system():
    return render_template("system.html")


class User(UserMixin):
    pass

# 通过用户名，获取用户记录，如果不存在，则返回None
def query_user(username):
    for user in users:
        if user['username'] == username:
            return user

# 如果用户名存在则构建一个新的用户类对象，并使用用户名作为ID
# 如果不存在，必须返回None
@login_manager.user_loader
def load_user(username):
    if query_user(username) is not None:
        curr_user = User()
        curr_user.id = username
        return curr_user
    # Must return None if username not found

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@app.route('/indexhoutai')
@login_required
def index():
    return render_template('indexhoutai.html')

@app.route('/home')
@fresh_login_required
def home():
    return 'Logged in as: %s' % current_user.get_id()


@app.route('/index',methods=["GET","POST"])
def form():
    if request.method == 'POST':
        username = request.form.get('fullname')
        user = query_user(username)
        print(username)
        # 验证表单中提交的用户名和密码
        if user is not None and request.form['fullpassword'] == user['password']:
            curr_user = User()
            curr_user.id = username

            # 通过Flask-Login的login_user方法登录用户
            login_user(curr_user, remember=True)

            # 如果请求中有next参数，则重定向到其指定的地址，
            # 没有next参数，则重定向到"index"视图
            next = request.args.get('next')
            return redirect(next or url_for('index'))
            #return render_template('hello.html')
        flash('Wrong username or password!')
    # GET 请求
    return render_template('index.html')

@app.route('/design',methods=['GET','POST'])
def design():
    tempdesigntag=maxtag
    conn = pymysql.connect(host='127.0.0.1', user='root', password='zys9970304', db='running', charset='utf8')
    cur = conn.cursor()
    sql = "select  * from runningdata "
    cur.execute(sql)
    u = cur.fetchall()
    conn.close()
    print(u)
    return render_template('design.html',u=u)

@app.route('/move',methods=['GET','POST'])
def move():
    return render_template('move.html')
def findmaxtag():
    conn=pymysql.connect(host='127.0.0.1',user='root',password='zys9970304',db='running',charset='utf8')
    cur=conn.cursor()
    sql=" select tag from runningdata where tag=(select max(tag) from runningdata)"
    cur.execute(sql)
    u=cur.fetchall()

    conn.close()
    return u

tem=findmaxtag()
global maxtag
maxtag=tem[0][0]
print(maxtag)
@app.route('/getmaxtag',methods=['GET','POST'])
def getmaxtag():
    u=findmaxtag()
    end=request.form.get('end')
    print(end)
    print(type(end))
    if end=='1':
        global maxtag
        temp=maxtag
        temp=temp+1
        maxtag=temp
    return "ok"
@app.route('/',methods=['GET','POST'])
def test():
    id=8888
    userid=50
    la = request.form.get('la')
    long=request.form.get('long')
    print(la)
    print(long)
    print(maxtag)
    insertdata = runningdata(id=id,la=la,long=long,tag=maxtag)
    db.session.add(insertdata)
    db.session.commit()
    return "ok"
app.secret_key = '1234567'
if __name__ == '__main__':
    app.run(debug=True)