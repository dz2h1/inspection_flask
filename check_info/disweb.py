# Author: dz2h1
import base64
import random

from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["info"]
db.authenticate(mongo_name(), mongo_password())


def password_encode(password):
    randnum = str(random.randint(100000, 999999))
    passrand = "".join([password, randnum])
    return base64.b64encode(passrand.encode()).decode()


def insert_info(info_name, info_add, info_usr, info_pw, info_port):
    info_password = password_encode(info_pw)
    coll.insert_one({
        "name": info_name,
        "address": info_add,
        "user": info_usr,
        "password": info_password,
        "port": info_port,
        "cpu": "timeout",
        "mem": "timeout",
        "disk": "timeout"
    })


def remove_info(info_del):
    coll.remove({"name": info_del})


def find_info_all():
    db_all = []
    for i in coll.find({}):
        db_all.append(i)
    return db_all
