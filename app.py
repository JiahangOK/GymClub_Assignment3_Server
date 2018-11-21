import base64
from io import BytesIO

from flask import Flask, send_from_directory, send_file, make_response

from flask import request
from flask.json import jsonify
from flask_script import Manager
import os
from flask_sqlalchemy import SQLAlchemy
from pandas import json
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import *


# 创建flask_sqlalchemy基于sqlite的实例db
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'userConfigBase.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

manager = Manager(app)
engine = create_engine('sqlite:///' + os.path.join(basedir, 'userConfigBase.sqlite'), echo=True)
metadata = MetaData(engine)
userdb = SQLAlchemy(app)

userName = ''
# 初始化数据库连接:
engine = create_engine('sqlite:///' + os.path.join(basedir, 'userConfigBase.sqlite'))
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


# 建立model类，用于创建table/model
class userInfoTable(userdb.Model):
    __tablename__ = 'userInfo'

    user_phone_number = userdb.Column(userdb.String, primary_key=True)
    user_email = userdb.Column(userdb.String, primary_key=True)
    username = userdb.Column(userdb.String)
    password = userdb.Column(userdb.String)
    pictureUrl = userdb.Column(userdb.String)

    def __repr__(self):
        return 'table name is ' + self.username

# 建立model类，用于创建table/model
class trainerInfoTable(userdb.Model):
    __tablename__ = 'trainerInfo'

    trainer_name = userdb.Column(userdb.String, primary_key=True)
    trainer_intro = userdb.Column(userdb.String, primary_key=True)
    def __repr__(self):
        return 'table name is ' + self.username


@app.route('/')
def test():
    return '服务器正常运行'


# show photo
@app.route('/userPicture', methods=['GET'])
def show_photo():
    if request.method == 'GET':
        filename = request.args.get('filename')
        if filename is None:
            pass
        else:
            image_data = open(os.path.join('./userPicture/','%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/jpeg'
            return response
    else:
        pass


# 用户登录 返回码为0无注册 返回码为1密码错误
@app.route('/user', methods=['POST'])
def check_user():
    haveregisted = userInfoTable.query.filter_by(username=request.form['username']).all()
    if haveregisted.__len__() is not 0:  # 判断是否已被注册
        passwordRight = userInfoTable.query.filter_by(username=request.form['username'],
                                                      password=request.form['password']).all()
        if passwordRight.__len__() is not 0:
            obj = userInfoTable.query.filter_by(username=request.form['username']).first()
            rootdir = obj.pictureUrl
            phonenum = obj.user_phone_number
            list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
            info_dict = {"info":[]}
            for i in range(0, len(list)):
                picture_file_name = list[i]
                # 图片文件
                path = os.path.join(rootdir, picture_file_name)
                if os.path.isfile(path):
                    # with open(path, 'rb') as f:
                    #     image_byte = base64.b64encode(f.read())
                    #     trainer_image_string = image_byte.decode('ascii')  # byte类型转换为str
                    trainer_name = picture_file_name.split(".")[0]
                    obj = trainerInfoTable.query.filter_by(trainer_name=trainer_name).first()
                    trainer_intro = obj.trainer_intro
                    print("trainer_name:",trainer_name)
                    trainer_image_url = "http://10.0.2.2:8080/userPicture?filename="+phonenum+"/"+picture_file_name
                    data = {"trainer_image_url": trainer_image_url,"trainer_name":trainer_name,"trainer_intro":trainer_intro}
                    info_dict.get("info").append(data)

            jsoninfo = json.dumps(info_dict)
            print("jsoninfo:",jsoninfo)
            return jsoninfo
        else:
            return '1'
    else:
        return '0'


# 用户注册
@app.route('/register', methods=['POST'])
def register():
    haveregisted = userInfoTable.query.filter_by(username=request.form['user_phone_number']).all()
    if haveregisted.__len__() is not 0:  # 判断是否已被注册
        return '0'

    pictureUrl = "./userPicture/" + request.form['user_phone_number']
    os.makedirs(pictureUrl)

    userInfo = userInfoTable(user_phone_number=request.form['user_phone_number'], user_email=request.form['user_email'],
                             username=request.form['username'], password=request.form['password'],
                             pictureUrl=pictureUrl)
    userdb.session.add(userInfo)
    userdb.session.commit()
    return '注册成功'


if __name__ == '__main__':
    userdb.create_all()  # 用来创建table，一般在初始化的时候调用
    app.run(host="127.0.0.1", port=8080, threaded=True)
