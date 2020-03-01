# Author: dz2h1
from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["dev"]
db.authenticate(mongo_name(), mongo_password())


def insert_dev(dev_name, dev_add):
    '''后台/console/插入dev设备使用'''
    coll.insert_one({"name": dev_name, "address": dev_add, "setdelay": "100"})


def remove_dev(dev_del):
    '''后台/console/删除dev设备使用'''
    coll.remove({"name": dev_del})


def find_all():
    '''为inspection_main和check_base提供查找dev库所有数据使用'''
    db_all = list(coll.find({}))
    return db_all
