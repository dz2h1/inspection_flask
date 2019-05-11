# Author: dz2h1
from config.settings import (logs_find_limit, mongo_clinet, mongo_name,
                             mongo_password)


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["logs"]
db.authenticate(mongo_name(), mongo_password())


def find_date():
    logs_date = []
    for i in coll.find({}):
        logs_date.append(i["date"])
    return logs_date


def find_svrstatus():
    logs_time = []
    for i in coll.find({}):
        logs_time.append(i["time"])
    return logs_time


def find_content():
    logs_content = []
    for i in coll.find({}):
        logs_content.append(i["content"])
    return logs_content


def find_all(find_limit=logs_find_limit):
    db_all = []
    for i in coll.find({}).sort("_id", -1).limit(find_limit):
        db_all.append(i)
    return db_all


def find_logs_num():
    return coll.find({}).count()


def del_logs(logs_num, logs_del_keepnum):

    if logs_del_keepnum < 0:
        logs_del_keepnum = 0

    logs_num -= logs_del_keepnum

    if logs_num < 0:
        logs_num = 0

    for i in range(logs_num):
        coll.find_one_and_delete({})
