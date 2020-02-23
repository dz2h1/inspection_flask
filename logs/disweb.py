# Author: dz2h1
from config.settings import (logs_find_limit, mongo_clinet, mongo_name,
                             mongo_password)


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["logs"]
db.authenticate(mongo_name(), mongo_password())


def find_all(find_limit=logs_find_limit):
    '''为/logs/页面提供全部log信息'''
    db_all = []
    for i in coll.find({}).sort("_id", -1).limit(find_limit):
        db_all.append(i)
    return db_all


def find_logs_num():
    '''为/console/后台提供log数量'''
    return coll.find({}).count()


def del_logs(logs_num, logs_del_keepnum):
    '''为/console/后台删除log'''
    if logs_del_keepnum < 0:
        logs_del_keepnum = 0

    logs_num -= logs_del_keepnum

    if logs_num < 0:
        logs_num = 0

    for i in range(logs_num):
        coll.find_one_and_delete({})
