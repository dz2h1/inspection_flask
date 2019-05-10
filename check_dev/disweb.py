# Author: dz2h1
from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["dev"]
db.authenticate(mongo_name(), mongo_password())


def find_name():
    names = []
    for i in coll.find({}):
        names.append(i["name"])
    return names


def find_status():
    status = []
    for i in coll.find({}):
        status.append(i["status"])
    return status


def find_delay():
    delay = []
    for i in coll.find({}):
        delay.append(i["delay"])
    return delay


def insert_dev(dev_name, dev_add):
    coll.insert_one({"name": dev_name, "address": dev_add})


def remove_dev(dev_del):
    coll.remove({"name": dev_del})


def find_all():
    db_all = []
    for i in coll.find({}):
        db_all.append(i)
    return db_all

