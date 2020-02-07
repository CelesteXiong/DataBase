from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager # manage our session
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

app.secret_key = 'super secret key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0925@127.0.0.1:3306/hunt_game'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
session_factory = sessionmaker(bind=engine)
session = flask_scoped_session(session_factory, app)



Time = 900
class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [
        {  # 第1个任务，每隔15min执行一次
            'id': 'hunt_treasure',
            'func': 'HuntGame.utils:hunt_treasure',  # 方法名
            'args': (),  # 入参
            'trigger': 'interval',  # interval表示循环任务
            'seconds': Time,  # 15min
        },
        {  # 第2个任务，每隔15min执行一次
            'id': 'work_money',
            'func': 'HuntGame.utils:work_money',  # 方法名
            'args': (),  # 入参
            'trigger': 'interval',  # interval表示循环任务
            'seconds': Time,  # 15min
        }
    ]

app.config.from_object(Config())  # 为实例化的flask引入配置

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from HuntGame import routes