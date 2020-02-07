from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from HuntGame import db
from HuntGame.models import Characters, Treasures
from datetime import datetime
from flask import jsonify
from HuntGame import app

MAX_TOOLS = 1
MAX_ACCESSORIES = 2


# 1. add character
def add_character(name, hashpass):
    money = 0
    character = Characters()
    character.cname = name
    character.password = hashpass
    character.money = money

    # db.session.begin() # no need
    db.session.add(character)
    db.session.commit()

    new_character = db.session.query(Characters).filter(Characters.cname == character.cname).one_or_none()
    print('new_character', new_character)
    print('type: ', type(new_character.cname))
    output = {'name': new_character.cname}
    return jsonify({'result': output})


# 3. count
def count_competence(character):
    # c_list =  [70, 120, 250, 450, 500]
    treasures = db.session.query(Treasures).filter(Treasures.cid == character.cid, Treasures.on_dress == True).all()
    num = len(treasures)
    if num == 0:
        score = 0
    elif num > 0:
        t_score = 0
        c_score = 0
        for t in treasures:
            t_score += t.competence_score
            c_score += t.luck_score
        score = (c_score * num + t_score) / (num)
    else:
        return None
    if score < MAX_COMPETENCE_SCORE:
        return score
    else:
        print("Treasure with wrong competence_score!")
        return None


def count_luck(character):
    treasures = db.session.query(Treasures).filter(Treasures.cid == character.cid, Treasures.on_dress == True).all()
    num = len(treasures)
    score = 0
    for t in treasures:
        score += t.luck_score
    if num:
        score = score / num
    else:
        sore = 0.2
    l_level = int(score)
    if l_level in treasures_luck_level:
        return l_level
    else:
        print("Treasure with wrong luck_score!!")
        return 0


def count_treasure(character):
    return len(db.session.query(Treasures).filter(Treasures.cid == character.cid).all())


# 3. work for money
def work_money():
    print(datetime.utcnow(), 'All characters auto-worked for money one time')

    for character in db.session.query(Characters).all():
        if character.competence <= 100:
            money = 101
        else:
            money = count_competence(character)

        character.money += money % 100
    print('All characters have worked one time!')
    return 0


# drop treasure with lowest luck
def throw_treasure(character):
    min_luck = max(treasures_luck_level) + 100
    throw_t = None
    for t in db.session.query(Treasures).filter(Treasures.cid == character.cid, Treasures.on_sale == False).all():
        if t.luck_score < min_luck:
            throw_t = t
    if throw_t is not None:
        print('Found throw_t with lowest luck!')
    else:
        return None
    db.session.query(Treasures).filter(Treasures.tid == throw_t.tid).delete(synchronize_session=False)
    db.session.commit()
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
    owner_id = character.cid
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
    new_t = Treasures(
        tname=new_name,
        luck_score=(1 + new_luck_score) * new_quality,
        competence_score=(28 + new_competence_score) * (1 - new_quality),
        on_sale=on_sale,
        price=price,
        cid=owner_id,
        on_dress=False
    )
    db.session.add(new_t)
    db.session.commit()

    new_t_t = db.session.query(Treasures).filter(Treasures.tname == new_name).all()
    new_id = new_t_t[0].tid
    if new_id is not None:
        print('Successfully generate a treasure into \'treasures\' collection!')
    # elif treasures.find({'name': new_name}).count() > 1:
    elif len(new_t_t) > 1:
        return jsonify({'Error': 'There exists two duplicated name in DB!'})
    return new_id


MAX_TREASURE = 20


def hunt_treasure():
    global MAX_TREASURE
    print(datetime.datetime.utcnow(), 'All characters auto-hunt for a treasure')

    for character in db.session.query(Characters).all():
        new_t_id = generate_treasure(character, character.competence_score, character.luck_score)
        if count_treasure(character) >= MAX_TREASURE:
            throw_t = throw_treasure(character)
            if throw_t is None:
                print('Hunt failed: the character\'s storage box is full of on-sale treasures')
                return 1
        # print("Successfully hunt a treasure")
    return 0


MAX_COMPETENCE_SCORE = max(treasures_competence_score)


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


def get_one_character(cname):
    print(cname)
    output = []
    name = cname
    for character in db.session.query(Characters).filter(Characters.cname == name).all():
        output.append({'id': str(character.cid),
                       'name': character.cname,
                       'money': character.money,
                       'competence_score': count_competence(character),
                       'luck_score': count_luck(character),
                       'number of treasures': count_treasure(character)
                       })
    if not output:
        output.append('Not find the character\'s name: {}'.format(name))
    return output


def get_all_characters():
    output = []
    for character in db.session.query(Characters).all():
        output.append({'id': str(character.cid),
                       'name': character.cname,
                       'money': character.money,
                       'competence_score': count_competence(character),
                       'luck_score': count_luck(character),
                       'number of treasures': count_treasure(character)
                       })
    return jsonify({'result': output})


def add_treasure_utils(treasure_name, name, competence_score, luck_score, on_sale, price):
    treasure_name = treasure_name
    owner_name = name
    owner = db.session.query(Characters).filter(Characters.cname == owner_name).one_or_none()
    if owner is None:
        return jsonify({'Error': 'The owner can\'t be found in database'})

    owner_id = owner.cid
    output = []
    if isinstance(treasure_name, list) is False:
        return jsonify({"Error: ": 'treasure_name is not a list'})
    for n in treasure_name:
        competence_score = competence_score
        luck_score = luck_score
        on_sale = on_sale
        price = price

        t = Treasures(
            tname=n,
            competence_score=competence_score,
            luck_score=luck_score,
            on_sale=on_sale,
            price=price,
            cid=owner_id
        )
        db.session.add(t)
        db.session.commit()

        new_t = db.session.query(Treasures).filter(Treasures.tid == t.tid).one_or_none()
        output.append({
            'tid': new_t.tid,
            'name': new_t.tname,
            'competence_score': new_t.competence_score,
            'luck_score': new_t.luck_score,
            'on_sale': new_t.on_sale,
            'price': new_t.price,
            'owner_id': owner_id
        })
    return output