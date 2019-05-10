# Author: dz2h1
from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["svr"]
size_coll = db["size"]
db.authenticate(mongo_name(), mongo_password())


def find_svrname():
    names = []
    for i in coll.find({}):
        names.append(i["name"])
    return names


def find_svrstatus():
    status = []
    for i in coll.find({}):
        status.append(i["status"])
    return status


def find_code():
    codes = []
    for i in coll.find({}):
        codes.append(i["code"])
    return codes


def find_all():
    db_all = []
    for i in coll.find({}):
        db_all.append(i)
    return db_all


def find_sizeall():
    db_sizeall = []
    for i in size_coll.find({}):
        db_sizeall.append(i)
    return db_sizeall


def insert_svr(svr_name, svr_add):
    coll.insert_one({"name": svr_name, "url": svr_add})


def remove_svr(svr_del):
    coll.remove({"name": svr_del})


def insert_size(size_name, size_add):
    size_coll.insert_one({
        "name": size_name,
        "url": size_add,
        "reference": 100
    })


def remove_size(size_del):
    size_coll.remove({"name": size_del})

