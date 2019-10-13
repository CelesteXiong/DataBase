import pymongo
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from bson import ObjectId
import datetime
from flask import Flask, jsonify, request,  url_for, session, redirect, Blueprint
import bcrypt
# url_for takes arguments and builds an endpoint, in this case we've just passed the name of a function,
# bp = Blueprint("mul", __name__, url_prefix="/cal")

client = pymongo.MongoClient(host='localhost')
db = client.Hunt_game
characters = db.characters
treasures = db.treasures

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def index():
    if 'username' in session:
        return 'You login as: ' + session['username']
    return "Please login in at http://localhost:5000/login."


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('login'))
    # return 'You have logged out!'


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.json['name']
        passwd = request.json['password']
        login_usr = characters.find_one({'name': str(username)})
        if login_usr:
            if bcrypt.hashpw(passwd.encode('utf-8'), login_usr['password']) == login_usr['password']:
                session['username'] = username
                return redirect(url_for(('index')))
        return 'Invalid combination of username and password!'
    else:
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # whether exists
        username = request.json['name']
        characters.find_one({'name': username})
        existing_user = characters.find_one({'name': username})
        if existing_user is None:  # register and login
            hashpass = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())
            # characters.insert_one({'name': username, 'password': hashpass})
            session['username'] = username
            add_character(username, hashpass)
            return redirect(url_for('login'))  # call the function of page
        return 'The username already exists!'
    # return render_template('register.html') # method == 'GET'
    return 'Please register'


# 1. characters
## 1.1 query
@app.route('/character', methods=['POST'])
def get_one_character():
    # name = request.args.get('name',default='', type = str)
    output = []
    name = request.json['name']
    for character in characters.find({'name': name}):
        output.append({'id': str(character['_id']),
                       'name': character['name'],
                       'date': character['date'],
                       'money': character['money'],
                       'treasure_dressed_id': [str(id) for id in character['treasure_dressed_id']],
                       'competence_score': character['competence_score'],
                       'luck_score': character['luck_score'],
                       'storage_box': [str(id) for id in character['storage_box']],
                       'count': character['count']
                       })
    if output == []:
        output = 'Not find the character\'s name: {}'.format(name)
    return jsonify({'result': output})


@app.route('/characters')
def get_all_characters():
    output = []
    for character in characters.find():
        output.append({'_id': str(character['_id']),
                       'name': character['name'],
                       'date': character['date'],
                       'money': character['money'],
                       'treasure_dressed_id': [str(id) for id in character['treasure_dressed_id']],
                       'competence_score': character['competence_score'],
                       'luck_score': character['luck_score'],
                       'storage_box': [str(id) for id in character['storage_box']],
                       'count': character['count']
                       })
    return jsonify({'result': output})


## 1.2 add characters
# @app.route('/characters/add', methods=['POST'])
def add_character(name, hashpass):
    # name = request.json['name']
    date = datetime.datetime.utcnow()
    money = 0
    treasure_dressed_id = []
    competence_score = 0
    luck_score = 0
    storage_box = []
    count = 0
    # player_name = session['name']
    character_id = characters.insert_one({
        'name': name,
        'password': hashpass,
        'date': date,
        'money': money,
        'treasure_dressed_id': treasure_dressed_id,
        'competence_score': competence_score,
        'luck_score': luck_score,
        'storage_box': storage_box,
        'count': count
    }).inserted_id
    new_character = characters.find_one({'_id': ObjectId(character_id)})

    output = {'name': new_character['name'], 'date': new_character['date']}
    return jsonify({'result': output})


## 1.3 work for money
def work_money():
    print(datetime.datetime.utcnow(), 'All characters auto-worked for money one time')

    for character in characters.find():
        if character['competence_score'] <= 100:
            money = 101
        else:
            money = character['competence_score']

        characters.update_one(
            {'_id': ObjectId(character['_id'])},
            {'$inc': {'money': (money % 100)}}
        )
        # print(character['money'])
    print('All characters have worked one time!')
    return 0


MAX_TOOLS = 1
MAX_ACCESSORIES = 2


## 1.4 dress on  a treasure
@app.route('/characters/dress/<task>', methods=['POST'])
def dress_treasure(task):
    # character_id = request.json['character_id']
    # name = session['username']
    name = request.json['name']
    character = characters.find_one({'name': name})
    character_id = str(character['_id'])
    t_list = request.json['treasure_name']
    # if isinstance(t_list, list):
    if len(t_list) > 3:
        print(len(t_list))
        return jsonify({'result': 'Number of treasures is out of bound{}!'.format(1)})
    else:
        output = []
        tools_num = 0
        accessorys_num = 0
        for dress_t_id in character['treasure_dressed_id']:
            dress_t = treasures.find_one({"_id": ObjectId(dress_t_id)})
            if dress_t['competence_score'] == 0:
                tools_num += 1
            elif dress_t['luck_score'] == 0:
                accessorys_num += 1
            else:
                return jsonify(
                    {'Error': "Treasure_id {}, name: {}, with wrong property".format(dress_t, dress_t['name'])})
        rest_tool = MAX_TOOLS - tools_num
        rest_accessory = MAX_ACCESSORIES - accessorys_num
        for t in t_list:
            new_dress_t = treasures.find_one({'name': t})
            if new_dress_t is None:
                return jsonify({"Error": "Treasure_name: {} is not found in DB".format(t)})
            t_id = str(new_dress_t['_id'])
            # storage_box = [str(id) for id in character['storage_box']]
            if new_dress_t is None or str(new_dress_t["owner_id"]) != str(character['_id']):
                print('Wrong treasure id {}'.format(t_id))
                continue
            if task == 'on':
                if new_dress_t['competence_score'] != 0 and rest_tool != 0:
                    rest_tool -= 1
                elif new_dress_t['luck_score'] != 0 and rest_accessory != 0:
                    rest_accessory -= 1
                else:
                    print('Number of dressed-on things has arrived the upper bound!')
                    continue
                new_competence_score = cal_competence(task, new_dress_t['competence_score'],
                                                      character['competence_score'],
                                                      len(character['treasure_dressed_id']))
                new_luck_score = cal_luck(task, new_dress_t['luck_score'], character['luck_score'],
                                          len(character['treasure_dressed_id']))
                if new_competence_score is None or new_luck_score is None:
                    return jsonify({'Error': 'Calculate wrong competence score or luck score!'})
                characters.update_one(
                    {'_id': ObjectId(character['_id'])},
                    {
                        '$addToSet':
                            {
                                'treasure_dressed_id': t_id
                            },
                        '$pull':
                            {
                                'storage_box': t_id
                            },
                        '$set':
                            {'competence_score':
                                 new_competence_score,
                             'luck_score':
                                 new_luck_score
                             }
                    }
                )
            elif task == 'off':
                take_off_t = treasures.find_one({'name': t})
                t_id = str(take_off_t['_id'])
                new_competence_score = cal_competence(task, take_off_t['competence_score'],
                                                      character['competence_score'],
                                                      len(character['treasure_dressed_id']))
                new_luck_score = cal_luck(task, take_off_t['luck_score'], character['luck_score'],
                                          len(character['treasure_dressed_id']))
                if new_competence_score is None or new_luck_score is None:
                    return jsonify({'Error': 'Calculate wrong competence score or luck score!'})
                characters.update_one(
                    {'_id': ObjectId(character['_id'])},
                    {
                        '$addToSet':
                            {
                                'storage_box': t_id
                            },
                        '$pull':
                            {
                                'treasure_dressed_id': t_id
                            },
                        '$set':
                            {'competence_score':
                                 new_competence_score,
                             'luck_score':
                                 new_luck_score
                             }
                    }
                )
        character = characters.find_one({"_id": ObjectId(character['_id'])})
        output.append(
            {'_id': str(character['_id']), 'name': character['name'], 'competence_score': character['competence_score'],
             'luck_score': character['luck_score'], 'treasure_dressed_id': character['treasure_dressed_id'],
             'storage_box': character['storage_box']})
        return jsonify({'Dress': output})


# treasuress
## 1. add
@app.route('/treasures/add', methods=['POST'])
def add_treasure():
    treasure_name = request.json['treasure_name']
    owner_name = request.json['name']
    owner = characters.find_one({'name': owner_name})
    if owner is None:
        return jsonify({'Error': 'The owner can\'t be found in database'})

    owner_id = str(owner['_id'])
    output = []
    if isinstance(treasure_name, list) is False:
        return jsonify({"Error: ": 'treasure_name is not a list'})
    for n in treasure_name:
        competence_score = request.json['competence_score']
        luck_score = request.json['luck_score']
        on_sale = False
        price = 0

        t_id = treasures.insert_one({
            'name': n,
            'competence_score': competence_score,
            'luck_score': luck_score,
            'on_sale': on_sale,
            'price': price,
            'owner_id': owner_id
        }).inserted_id
        new_t = treasures.find_one({'_id': ObjectId(t_id)})
        output.append({
            'name': new_t['name'],
            'competence_score': new_t['competence_score'],
            'luck_score': new_t['luck_score'],
            'on_sale': new_t['on_sale'],
            'price': new_t['price'],
            'owner_id': owner_id
        })
    return jsonify({'result': output})


## 2. character obtain one treasure
### 2.1 auto-from hunting
from flask_apscheduler import APScheduler

Time = 900
class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [
        {  # 第1个任务，每隔15min执行一次
            'id': 'hunt_treasure',
            'func': '__main__:hunt_treasure',  # 方法名
            'args': (),  # 入参
            'trigger': 'interval',  # interval表示循环任务
            'seconds': Time,  # 15min
        },
        {  # 第2个任务，每隔15min执行一次
            'id': 'work_money',
            'func': '__main__:work_money',  # 方法名
            'args': (),  # 入参
            'trigger': 'interval',  # interval表示循环任务
            'seconds': Time,  # 15min
        }
    ]


app.config.from_object(Config())  # 为实例化的flask引入配置


# drop treasure with lowest luck
def throw_treasure(character):
    min_luck = max(treasures_luck_level) + 100
    for t_id in character['storage_box']:
        t = treasures.find_one({'_id': ObjectId(t_id), 'on_sale': False})
        if t['luck_score'] < min_luck:
            throw_t = t
    if throw_t is None: print('Found throw_t with lowest luck!')
    treasures.update_one(
        {'_id': ObjectId(throw_t['_id'])},
        {'$set':
             {'owner_id': None,
              'on_sale': False,
              'price': 0
              }
         }
    )
    characters.update_one(
        {'_id': ObjectId(character['_id'])},
        {
            '$pull':
                {
                    'storage_box': throw_t
                },
            '$inc':
                {
                    'count': -1,
                }
        }
    )
    return throw_t


### 2.2 generate treasure

from random import choice

treasure_names_list = ['烛龙', '帝江', '英招', '饕餮', '白泽', '应龙', '九尾狐', '青鸟', '狻猊', '穷奇', '凤凰']
treasures_luck_level = [num for num in range(50)] 
treasures_competence_score = [0, 28, 70, 96, 120, 250, 345, 427, 513, 624, 718]

quantile_15 = 0.25
quantile_25 = 0.35
quantile_50 = 0.5
quantile_75 = 0.75
quantile_95 = 0.95

quality = [0, 1]


def generate_treasure(character, competence_score, luck_score):
    if character is None:
        return jsonify({'Error': 'The character is None!'})
    on_sale = False
    price = 0
    owner_id = str(character['_id'])
    luck_idx = treasures_luck_level.index(luck_score)
    luck_loc = luck_idx // len(treasures_luck_level)

    if luck_loc >= quantile_95:
        new_quantile = 0.99
    elif luck_loc >= quantile_75:
        new_quantile = quantile_95
    elif luck_loc >= quantile_50:
        new_quantile = quantile_75
    elif luck_loc >= quantile_25:
        new_quantile = quantile_50
    elif luck_loc >= quantile_15:
        new_quantile = quantile_25
    else:
        new_quantile = 0.25
    new_competence_score = choice(treasures_competence_score[0:int(len(treasures_competence_score) * new_quantile)])
    new_luck_score = choice(treasures_luck_level[0:int(len(treasures_luck_level) * new_quantile)])
    new_quality = choice(quality)
    new_name = choice(treasure_names_list) + str(datetime.datetime.utcnow())
    new_t = {
        'name': new_name,
        'luck_score': (1 + new_luck_score) * new_quality,
        'competence_score': (28 + new_competence_score) * (1 - new_quality),
        'on_sale': on_sale,
        'price': price,
        'owner_id': owner_id
    }
    new_id = treasures.insert_one(new_t).inserted_id
    if new_id is not None:
        print('Successfully generate a treasure into \'treasures\' collection!')
    elif treasures.find({'name': new_name}).count() > 1:
        return jsonify({'Error':'There exists two duplicated name in DB!'})
    return new_id


MAX_TREASURE = 20


def hunt_treasure():
    global MAX_TREASURE
    print(datetime.datetime.utcnow(), 'All characters auto-hunt for a treasure')

    for character in characters.find():
        new_t_id = generate_treasure(character, character['competence_score'], character['luck_score'])
        if character['count'] >= MAX_TREASURE:
            throw_t = throw_treasure(character)
            if throw_t is None:
                print('Hunt failed: the character\'s storage box is full of on-sale treasures')
                return 1
        characters.update_one(
            {'_id': ObjectId(character['_id'])},
            {'$addToSet': {'storage_box': str(new_t_id)},  # add a value, unless exists
             '$inc': {'count': 1}
             }
        )
        # print("Successfully hunt a treasure")
    return 0


MAX_COMPETENCE_SCORE = max(treasures_competence_score)


# @app.route('/treasures/hunt', methods=['POST'])
def cal_competence(task, t_score, c_score, num):
    # c_list =  [70, 120, 250, 450, 500]
    if task == 'on':
        score = (c_score * num + t_score) / (num + 1)
    elif task == 'off':
        if num == 1:
            score = 0
        elif num < 0:
            return None
        else:
            score = (c_score * num - t_score) / (num - 1)
    if score < MAX_COMPETENCE_SCORE:
        return score
    else:
        print("Treasure with wrong competence_score!")
        return None


#  treasures_luck_level = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
def cal_luck(task, t_score, c_score, num):
    if task == 'on':
        print(t_score, c_score, num)
        score = (c_score * num + t_score) / (num + 1)
    elif task == 'off':
        if num == 1:
            score = 0
        else:
            score = (c_score * num - t_score) / (num - 1)
    l_level = int(score)
    if l_level in treasures_luck_level:
        return l_level
    else:
        print("Treasure with wrong luck_score!!")
        return 0


### 2.3 query
@app.route('/treasures')
def get_all_treasures():
    output = []
    for t in treasures.find():
        output.append({
            'id': str(t['_id']),
            'name': t['name'],
            'competence_score': t['competence_score'],
            'luck_score': t['luck_score'],
            'on_sale': t['on_sale'],
            'price': t['price'],
            'owner_id': str(t['owner_id'])
        })
    return jsonify({'result': output})


# Market
## 1. query all on-sale treasures
@app.route('/market')
def get_all_onsale_treatutes():
    output = []
    for onsale_t in treasures.find({'on_sale': True}):
        output.append({
            'name': onsale_t['name'],
            'competence_score': onsale_t['competence_score'],
            'luck_score': onsale_t['luck_score'],
            'on_sale': onsale_t['on_sale'],
            'price': onsale_t['price'],
            'owner_id': str(onsale_t['owner_id'])
        })
    return jsonify({'All on-sale treasures': output})


## 2. put treasures into market
@app.route('/market/transaction/<task>', methods=['POST'])
def transaction_treasures(task):
    # task = request.json['task']
    # default: character is a buyer, so 'name' in fact is for buyer
    character_name = request.json['name']
    character = characters.find_one({'name': character_name})

    t_name = request.json['treasure_name']
    t = treasures.find_one({'name': t_name})
    # print(t)

    output = []
    if character['_id'] is None:
        return jsonify({'result': 'character_id is invalid!'})
    elif t is None:
        return jsonify({'result': 'treasure_id is invalid!'})
    else:
        if task == 'purchase':
            if t['on_sale'] is False:
                print(t)
                return jsonify({'result': 'treasure is not on_sale now!'})
            elif t['price'] > character['money']:
                return jsonify({'result': 'you have money:{}, which is less than the  price:{}'.format(
                    character['money'], t['price'])})
            if character['count'] >= MAX_TREASURE:
                throw_treasure(character)
            seller = characters.find_one({'_id': ObjectId(t['owner_id'])})
            characters.update_one(
                {'_id': ObjectId(seller['_id'])},
                {'$inc':
                    {
                        'count': -1,
                        'money': t['price']
                    },
                    '$pull':
                        {
                            'storage_box': str(t['_id'])
                        }
                }
            )
            characters.update_one(
                {'_id': ObjectId(character['_id'])},
                {
                    '$addToSet':
                        {
                            'storage_box': str(t['_id'])
                        },
                    '$inc':
                        {
                            'count': 1,
                            'money': -t['price'],
                        }
                }
            )
            treasures.update_one(
                {'_id': ObjectId(t['_id'])},
                {'$set':
                    {
                        'on_sale': False,
                        'price': 0,
                        'owner_id': str(character['_id'])
                    }
                }
            )
        if task == 'for_sale':  # 只是挂牌，不是售出
            if t['on_sale'] is True:
                return jsonify({"result": 'treasure has been on_sale!'})
            elif str(t['owner_id']) != str(character['_id']):
                return jsonify(({'error': 'treasure isn\'t in yout storage_box!'}))
            treasures.update_one(
                {'_id': ObjectId(t['_id'])},
                {'$set':
                    {
                        'on_sale': True,
                        'price': request.json['price']
                    }
                }
            )
        if task == 'off_sale':
            if t['on_sale'] is False:
                return jsonify({'result': 'the treasure has been off_sale!'})
            elif str(t['owner_id']) != str(character['_id']):
                return jsonify(({'error': 'treasure isn\'t in yout storage_box!'}))
            treasures.update_one(
                {'_id': ObjectId(t['_id'])},
                {'$set':
                    {
                        'on_sale': False,
                        'price': 0
                    }
                }
            )
        t = treasures.find_one({'_id': ObjectId(t['_id'])})
        output.append({
            'user_id': str(character['_id']),
            'owner_name': character['name'],
            'treasure_name': t['name'],
            'treasure_id': str(t['_id']),
            'owner_id': str(t['owner_id']),
            'on_sale': t['on_sale'],
            'price': t['price'],
            'money': character['money']
        })
        return jsonify({task: output})


def test_auto_jobs():

    with app.app_context():
        for job_id in scheduler.get_jobs():
            print(job_id)
            print(job_id.next_run_time)

            # assert job_id.next_run_time.replace(tzinfo=None) >= (datetime.datetime.utcnow() + datetime.timedelta(minutes=15)).replace(tzinfo =None)
            # assert job_id.next_run_time.replace(tzinfo=None) <= (datetime.datetime.utcnow() + datetime.timedelta(minutes=15)).replace(tzinfo =None)


def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')


def return_app():
    return app

if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    # Add event listener
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    app.secret_key = 'mysecret'
    test_auto_jobs()
    app.run(debug=True)


