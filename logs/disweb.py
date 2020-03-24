# Author: dz2h1
from pymongo import DeleteOne
from config.settings import (logs_find_limit, mongo_clinet, mongo_name,
                             mongo_password)


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["logs"]
db.authenticate(mongo_name(), mongo_password())


def find_all(page_num=1, find_limit=logs_find_limit):
    '''为/logs/页面提供全部log信息'''
    num = (page_num - 1) * logs_find_limit
    db_all = list(coll.find({}).sort("_id", -1).skip(num).limit(find_limit))
    return db_all


def find_logs_num():
    '''为/console/后台提供log数量'''
    return coll.count_documents({})


def del_logs(logs_num, logs_del_keepnum):
    '''为/console/后台删除log'''
    arr = []
    if logs_del_keepnum < 0:
        logs_del_keepnum = 0
    logs_num -= logs_del_keepnum
    if logs_num > 0:
        for _ in range(logs_num):
            arr.append(DeleteOne({}))
        coll.bulk_write(arr)
