from werkzeug.routing import ValidationError

from HuntGame import app, bcrypt, db
from flask import jsonify, request, url_for, session, redirect, flash
from HuntGame.utils import *
from HuntGame.models import Characters, Treasures
from flask_login import login_user, current_user, logout_user

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        # whether exists
        username = request.json['name']
        existing_user = db.session.query(Characters).filter(Characters.cname == username).one_or_none()
        # print(username)
        print('existing_user', existing_user)

        if existing_user is None:  # register and login
            hashpass = bcrypt.generate_password_hash(request.json['password']).decode(
                'utf-8')  # want a string instead of a byte
            add_character(username, hashpass)
            flash('Your account has been created!')
            return redirect(url_for('login'))  # call the function of page
        else:
            raise ValidationError('The username already exists! Please choose a different one.')
            return;
    return 'Please register'


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    elif request.method == 'POST':
        username = request.json['name']
        passwd = request.json['password']
        login_usr = db.session.query(Characters).filter(Characters.cname == username).one_or_none()

        if login_usr and bcrypt.check_password_hash(login_usr.password, passwd):
            # log character in
            login_user(login_usr, remember=True)
            # remember = True A cookie will be saved on the user's computer, and then Flask-Login will automatically
            # restore the user ID from that cookie if it is not in the session.
            return redirect(url_for(('home')))
        else:
            flash('Invalid combination of username and password!')
    else:
        return redirect(url_for('index'))


@app.route('/', methods=["GET", "POST"])
def index():
    if 'username' in session:
        return 'You login as: ' + session['username']
    return "Welcome! Please log in."


@app.route('/home', methods=["GET", "POST"])
def home():
    output = []
    output.append(get_one_character(current_user.cname))
    return jsonify({'HomePage':output})


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('You have logged out!')
    return redirect(url_for('index'))


# 1. characters

## 1.4 dress on  a treasure
@app.route('/characters/dress/<task>', methods=['POST'])
def dress_treasure(task):
    name = request.json['name']
    character = db.session.query(Characters).filter(Characters.cname == name).one_or_none()
    # character_id = character.cid
    t_list = request.json['treasure_name']
    # if isinstance(t_list, list):
    if len(t_list) > 3:
        print(len(t_list))
        return jsonify({'result': 'Number of treasures is out of bound{}!'.format(3)})
    else:
        output = []
        tools_num = 0
        accessorys_num = 0
        for dress_t in db.session.query(Treasures).filter(Treasures.cid == character.cid).all():
            if count_competence(dress_t) == 0:
                tools_num += 1
            elif count_luck(dress_t) == 0:
                accessorys_num += 1
            else:
                return jsonify(
                    {'Error': "Treasure_id {}, name: {}, with wrong property".format(dress_t.tid, dress_t.tname)})
        rest_tool = MAX_TOOLS - tools_num
        rest_accessory = MAX_ACCESSORIES - accessorys_num
        for t in t_list:
            new_t = db.session.query(Treasures).filter(Treasures.tname == t).one_or_none()
            if new_t is None:
                return jsonify({"Error": "Treasure_name: {} is not found in DB".format(t)})

            if new_t is None or new_t.cid != character.cid:
                print('Wrong treasure id {}'.format(t.tid))
                continue
            if task == 'on':
                if new_t.competence_score != 0 and rest_tool != 0:
                    rest_tool -= 1
                elif new_t.luck_score != 0 and rest_accessory != 0:
                    rest_accessory -= 1
                else:
                    print('Number of on_dress things has arrived the upper bound!')
                    continue

                new_t.on_dress = True

                db.session.merge(new_t)
                db.session.commit()
            elif task == 'off':

                new_t.on_dress = False
                db.session.merge(new_t)
                db.session.commit()

        character = db.session.query(Characters).filter(Characters.cid == character.cid).one_or_none()
        output.append(
            {'cid': character.cid,
             'cname': character.cname,
             'competence_score': count_competence(character),
             'luck_score': count_luck(character),
             'on_dress': [t.tname for t in db.session.query(Treasures).filter(Treasures.cid == character.cid,
                                                                              Treasures.on_dress == True).all()],
             'off_dress': [t.tname for t in db.session.query(Treasures).filter(Treasures.cid == character.cid,
                                                                               Treasures.on_dress == False).all()]
             }
        )
        return jsonify({'Dress': output})


# treasuress
## 1. add
@app.route('/treasures/add', methods=['POST'])
def add_treasure():
    treasure_name_list = request.json['treasure_name']
    owner_name = request.json['name']
    owner = db.session.query(Characters).filter(Characters.cname == owner_name).one_or_none()
    if owner is None:
        return jsonify({'Error': 'The owner can\'t be found in database'})

    owner_id = owner.cid
    output = []
    if isinstance(treasure_name_list, list) is False:
        return jsonify({"Error: ": 'treasure_name is not a list'})
    competence_score = request.json['competence_score']
    luck_score = request.json['luck_score']
    on_sale = request.json['on_sale']
    price = request.json['price']
    output = add_treasure_utils(treasure_name_list, owner_name, competence_score, luck_score, on_sale, price)
    return jsonify({'Add treasure:': output})

# Market
## 1. query all on-sale treasures
@app.route('/market')
def get_all_onsale_treatures():
    output = []
    for onsale_t in db.session.query(Treasures).filter(Treasures.on_sale == True).all():
        output.append({
            'name': onsale_t.tname,
            'competence_score': onsale_t.competence_score,
            'luck_score': onsale_t.luck_score,
            'on_sale': onsale_t.on_sale,
            'price': onsale_t.price
        })
    return jsonify({'All on-sale treasures': output})


## 2. put treasures into market
@app.route('/market/transaction/<task>', methods=['POST'])
def transaction_treasures(task):
    character_name = request.json['name']
    character = db.session.query(Characters).filter(Characters.cname == character_name).one_or_none()

    t_name = request.json['treasure_name']
    t = db.session.query(Treasures).filter(Treasures.tname == t_name).one_or_none()

    output = []
    if character.cid is None:
        return jsonify({'result': 'character_id is invalid!'})
    elif t is None:
        return jsonify({'result': 'treasure_id is invalid!'})
    else:
        if task == 'purchase':
            if t.on_sale is False:
                print(t)
                return jsonify({'result': 'treasure with ID: {} is not on_sale now!'.format(t.tid)})
            elif t.price > character.money:
                return jsonify({'result': 'you have money:{}, which is less than the  price:{}'.format(
                    character.money, t.price)})
            if count_treasure(character) >= MAX_TREASURE:
                throw_treasure(character)

            seller = db.session.query(Characters).filter(Characters.cid == t.cid).one_or_none()
            seller.money += t.price
            character.money -= t.price
            print(t.cid)
            t.cid = character.cid
            print(t.cid)
            t.on_sale = False
            t.price = 0
            # db.session.merge(seller)

        if task == 'for_sale':  # 只是挂牌，不是售出

            if t.on_sale is True:
                return jsonify({"result": 'treasure has been on_sale!'})
            elif t.cid != character.cid:
                return jsonify(({'error': 'treasure isn\'t in yout storage_box!'}))
            t.on_sale = True
            t.price = request.json['price']

        if task == 'off_sale':
            if t.on_sale is False:
                return jsonify({'result': 'the treasure has been off_sale!'})
            elif t.cid != character.cid:
                return jsonify(({'error': 'treasure isn\'t in yout storage_box!'}))
            t.on_sale = False
            t.price = 0

        db.session.merge(t)
        db.session.merge(character)
        db.session.commit()

        t = db.session.query(Treasures).filter(Treasures.tid == t.tid).one_or_none()
        # t = treasures.find_one({'_id': ObjectId(t['_id'])})
        output.append({
            'user_id': character.cid,
            'owner_name': character.cname,
            'treasure_name': t.tname,
            'treasure_id': t.tid,
            'owner_id': t.cid,
            'on_sale': t.on_sale,
            'price': t.price,
            'money': character.money
        })
        return jsonify({task: output})
