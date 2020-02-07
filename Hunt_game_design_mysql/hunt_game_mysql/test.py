import requests, datetime

from run import app  # goes into __init__ in HuntGame to grab app
from HuntGame.models import Characters, Treasures
from HuntGame.utils import *
import time
from flask_sqlalchemy_session import current_session

URL = 'http://127.0.0.1:5000/'


def verify_json_register(name, current_session):
    current_session.commit()
    assert current_session.query(Characters).filter(Characters.cname == name).one_or_none()


def test_register(current_session):
    url = URL + 'register'

    time_t = datetime.utcnow()
    t_name = str(time.mktime(time_t.timetuple()))

    passwd = "test_register"
    dicTosend = {"name": t_name, "password": passwd}
    res = requests.post(url, json=dicTosend)

    print("Response from the server: ", res.text)
    verify_json_register(t_name, current_session)
    return t_name, passwd


def test_login(current_session):
    url_in = URL + 'login'
    url_out = URL + 'logout'

    print('First, register to create an existing account: ')
    name, password = test_register(current_session)
    print('Then log in: ')
    dicTosend = {"name": name, "password": password}
    res_login = requests.post(url_in, json=dicTosend)
    res_logout = requests.get(url_out)
    print('Response: ', res_login.text)
    print('Finally log out.')
    print('Response: ', res_logout.text)


def test_logout():
    url = URL + 'login'
    print('First register to create an existing account: ')
    url = URL + 'logout'
    res = requests.get(url)
    print('After logout:')
    print("Response from the server: ", res.text)


#  task: on/off
#  treasure_names_list = ['烛龙', '帝江', '英招', '饕餮', '白泽', '应龙', '九尾狐', '青鸟', '狻猊', '穷奇', '凤凰']
#  treasures_luck_level = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#  treasures_competence_score = [0, 28, 70, 96, 120, 250, 345, 427, 513, 624, 718]
def test_dress_treasure(task, current_session, name=None, treasure_name_list=None):
    #  task: on/off
    def verify_dress_treasure():
        character = current_session.query(Characters).filter(Characters.cname == name).one_or_none()
        assert character
        for treasure_name in treasure_name_list:
            print(treasure_name)
            current_session.commit()
            t = current_session.query(Treasures).filter(Treasures.tname == treasure_name).one_or_none()
            print(t)
            assert t is not None
            if task == "on":
                assert t.tid in [on_t.tid for on_t in current_session.query(Treasures).filter(Treasures.tid == t.tid,
                                                                                              Treasures.on_dress == True).all()]
            if task == "off":
                assert t.tid in [on_t.tid for on_t in current_session.query(Treasures).filter(Treasures.tid == t.tid,
                                                                                              Treasures.on_dress == False).all()]

    if name is None:
        name, passwd = test_register(current_session)

    url = URL + 'characters/dress/' + task
    if treasure_name_list is None:
        url_add_t = URL + 'treasures/add'
        treasure_name_list = [
            'Test_treasure' + str(datetime.utcnow())]  # list for dressing more than one treasures
        competence_score = 0
        luck_score = 3
        price = 0
        on_dress = False
        on_sale = False
        res_add_t = requests.post(url_add_t,
                                  json={'name': name, 'treasure_name': treasure_name_list,
                                        'competence_score': competence_score,
                                        'luck_score': luck_score,
                                        'on_dress': on_dress,
                                        'on_sale': on_sale,
                                        'price': price})
        print("Response for adding a treasure: ", res_add_t.text)

    res_dress_t = requests.post(url, json={'name': name, 'treasure_name': treasure_name_list})
    print("Response for dressing a treasure: ", res_dress_t.text)
    verify_dress_treasure()


def test_transaction(task, current_session, treasure_name=None, name=None, price=0):
    #  task: purchase/for_sale/off_sale
    def verify_transaction(task, t_name, user_name, t_price):
        current_session.commit()
        t = current_session.query(Treasures).filter(Treasures.tname == t_name).one_or_none()
        character = current_session.query(Characters).filter(Characters.cname == user_name).one_or_none()
        assert t
        assert character
        if task == 'for_sale':
            assert t.on_sale == True
            assert t.price == price
        if task == 'purchase':
            t = current_session.query(Treasures).filter(Treasures.tname == t.tname).one_or_none()
            purchaser = current_session.query(Characters).filter(Characters.cname == user_name).one_or_none()
            assert t.tid in [on_t.tid for on_t in
                             current_session.query(Treasures).filter(Treasures.cid == purchaser.cid).all()]

        if task == 'off_sale':
            assert t.price == 0
            assert t.on_sale == False

    url = URL + 'market/transaction/' + task
    if name is None:
        #  create a character
        name, passwd = test_register(current_session)

    if treasure_name is None:
        #  add a treasure to 2 characters
        url_add_t = URL + 'treasures/add'
        treasure_name = 'Test_treasure: ' + str(datetime.utcnow())
        competence_score = 0
        luck_score = 3

        if task == 'off_sale':
            on_sale = True
            price = 0
        if task == 'purchase':
            on_sale = True
            price = 0.0001
        elif task == 'for_sale':
            on_sale = False
            price = 0

        res_add_t = requests.post(url_add_t,
                                  json={'name': name, 'treasure_name': [treasure_name],
                                        'competence_score': competence_score,
                                        'luck_score': luck_score,
                                        'price': price,
                                        'on_sale': on_sale
                                        })
        print("Response for adding a treasure: ", res_add_t.text)
    dictTosend = {}
    if task == 'off_sale':
        dictTosend = {'treasure_name': treasure_name, 'name': name}
    elif task == 'purchase':
        # create a character to have enough money to buy this treasure
        time.sleep(1)
        p_name, p_passwd = test_register(current_session)
        purchaser = current_session.query(Characters).filter(Characters.cname == p_name).one_or_none()
        purchaser.money = 100
        current_session.merge(purchaser)
        current_session.commit()
        dictTosend = {'treasure_name': treasure_name, 'name': purchaser.cname}
        name = purchaser.cname
    elif task == 'for_sale':
        dictTosend = {'treasure_name': treasure_name, 'name': name, 'price': price}

    res = requests.post(url, json=dictTosend)
    print("Response for transaction task {} : ".format(task), res.text)
    verify_transaction(task, treasure_name, name, price)


def show_market():
    url = URL + 'market'
    res = requests.get(url)
    print("Market: ", res.text)


def test_get_one_character(name=None):
    url = URL + 'character'
    if name is None:
        name, password = test_register()
    dicTodend = {"name": name}
    res = requests.post(url, json=dicTodend)
    print("test_get_one_character: ", res.text)
    print(res.json())


def test_get_all_characters():
    url = URL + 'characters'
    res = requests.get(url)
    print("test_get_all_characters: ", res.text)
    print(res.json())


if __name__ == '__main__':
    with app.app_context():
        # db.session = current_session
        #  test_register(current_session)
        test_login(current_session)# log in contains log out and register
        test_dress_treasure('on', current_session)

        time.sleep(1)
        test_dress_treasure('off', current_session)

        time.sleep(1)
        test_transaction('for_sale', current_session)

        time.sleep(1)
        test_transaction('purchase', current_session)

        time.sleep(1)
        test_transaction('off_sale', current_session)

        print('show market: \n')
        show_market()
