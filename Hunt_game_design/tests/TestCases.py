import bcrypt
import requests, datetime
from bson import ObjectId
from flask.testing import FlaskClient
import pymongo

URL = 'http://localhost:5000/'
Mongo_client = pymongo.MongoClient(host='localhost')
db = Mongo_client.Hunt_game
characters = db.characters
treasures = db.treasures


def verify_json_register(name):
    assert characters.find_one({"name": name})


def test_register():
    # name, password
    url = URL + 'register'
    name = str(datetime.datetime.utcnow())
    passwd = "test_register"
    dicTosend = {"name": name, "password": passwd}
    res = requests.post(url, json=dicTosend)
    print("Response from the server: ", res.text)

    verify_json_register(name)
    return name, passwd


def test_login():
    url = URL + 'login'
    print('First register to create an existing account: ')
    name, password = test_register()
    print('Then log in: ')
    dicTosend = {"name": name, "password": password}
    res = requests.post(url, json=dicTosend)
    print(res.text)


def test_logout():
    # name, password
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
def test_dress_treasure(task, name=None, treasure_name_list=None):
    #  task: on/off
    def verify_dress_treasure(task, name, treasure_name_list):
        character = characters.find_one({"name": name})
        assert character
        for treasure_name in treasure_name_list:
            t = treasures.find_one({"name": treasure_name})
            assert t
            assert t['owner_id']
            if task == "on":
                assert str(t['_id']) in [str(t_id) for t_id in character['treasure_dressed_id']]
            if task == "off":
                assert str(t['_id']) in [str(t_id) for t_id in character['storage_box']]

    if name is None:
        name, passwd = test_register()
    url = URL + 'characters/dress/' + task
    if treasure_name_list is None:
        url_add_t = URL + 'treasures/add'
        treasure_name_list = [
            'Test_treasure' + str(datetime.datetime.utcnow())]  # list for dressing more than one treasures
        competence_score = 0
        luck_score = 3
        res_add_t = requests.post(url_add_t,
                                  json={'name': name, 'treasure_name': treasure_name_list,
                                        'competence_score': competence_score,
                                        'luck_score': luck_score})
        print("Response for adding a treasure: ", res_add_t.text)

    res_dress_t = requests.post(url, json={'name': name, 'treasure_name': treasure_name_list})
    print("Response for dressing a treasure: ", res_dress_t.text)
    verify_dress_treasure(task, name, treasure_name_list)


def test_transaction(task, treasure_name=None, name=None, price=0):
    #  task: purchase/for_sale/off_sale
    def verify_transaction(task, t_name, user_name, t_price):
        t = treasures.find_one({'name': t_name})
        character = characters.find_one({"name": user_name})
        assert t
        assert character
        if task == 'for_sale':
            assert t['on_sale'] == True
            assert t['price'] == price
        if task == 'purchase':
            #  make some treasure on_sale
            treasures.update_one(
                {'_id': ObjectId(t['_id'])},
                {'$set':
                    {
                        'on_sale': True,
                        'price': price
                    }
                }
            )
            on_sale_t = treasures.find_one({'on_sale': True})
            #  create a purchase to buy treasure with treasure_name from the owner name
            purchaser = characters.find_one()
            dict = {'treasure_name': on_sale_t['name'], 'name': purchaser['name']}
            requests.post(URL + 'market/transaction/purchase', json=dict)
            print(on_sale_t)
            #  update purchaser
            purchaser = characters.find_one({'name': purchaser['name']})

            assert str(on_sale_t['_id']) in [str(t_id) for t_id in purchaser['storage_box']]

        if task == 'off_sale':
            assert t['price'] == 0
            assert t['on_sale'] == False

    url = URL + 'market/transaction/' + task

    if name is None:
        #  create a character
        name, passwd = test_register()
    if treasure_name is None:
        #  add a treasure to 2 characters
        url_add_t = URL + 'treasures/add'
        treasure_name = 'Test_treasure: ' + str(datetime.datetime.utcnow())
        competence_score = 0
        luck_score = 3
        res_add_t = requests.post(url_add_t,
                                  json={'name': name, 'treasure_name': [treasure_name],
                                        'competence_score': competence_score,
                                        'luck_score': luck_score})
        print("Response for adding a treasure: ", res_add_t.text)
    dictTosend = {}
    if task == 'purchase' or task == 'off_sale':
        dictTosend = {'treasure_name': treasure_name, 'name': name}
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
    test_register()
    test_login()
    test_logout()

    test_dress_treasure('on')
    test_dress_treasure('off')

    test_transaction('for_sale')
    test_transaction('purchase')
    test_transaction('off_sale')

    print('show market: \n')
    show_market()
