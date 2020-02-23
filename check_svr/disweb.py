# Author: dz2h1
from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["svr"]
size_coll = db["size"]
db.authenticate(mongo_name(), mongo_password())


def find_all():
    '''为inspection_main和check_base提供查找svr库所有数据使用'''
    db_all = []
    for i in coll.find({}):
        db_all.append(i)
    return db_all


def find_sizeall():
    '''为inspection_main和check_base提供查找size库所有数据使用'''
    db_sizeall = []
    for i in size_coll.find({}):
        db_sizeall.append(i)
    return db_sizeall


def insert_svr(svr_name, svr_add):
    '''后台/console/插入svr设备使用'''
    coll.insert_one({"name": svr_name, "url": svr_add})


def remove_svr(svr_del):
    '''后台/console/删除svr设备使用'''
    coll.remove({"name": svr_del})


def insert_size(size_name, size_add):
    '''后台/console/插入size页面使用'''
    size_coll.insert_one({
        "name": size_name,
        "url": size_add,
        "reference": 100
    })


def remove_size(size_del):
    '''后台/console/删除size页面使用'''
    size_coll.remove({"name": size_del})
