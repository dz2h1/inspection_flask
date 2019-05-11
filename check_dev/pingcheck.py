# Author: dz2h1
import gevent
from gevent import monkey; monkey.patch_all()

import os
import re

from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["dev"]
db.authenticate(mongo_name(), mongo_password())
pi = "ping -c 1 -w 2 "


def find_ip():
    ips = []
    for i in coll.find({}):
        ips.append(i["address"])
    return ips


def find_dev_names():
    names = []
    for i in coll.find({}):
        names.append(i["name"])
    return names


def find_dev_names_ips():
    names = []
    ips = []
    alls = []
    for i in coll.find({}):
        names.append(i["name"])
        ips.append(i["address"])
    alls = zip(names, ips)
    return alls


def change_status(ip, sta):
    coll.update_one({"address": ip}, {"$set": {"status": sta}})


def change_delay(ip, time):
    coll.update_one({"address": ip}, {"$set": {"delay": time}})


def check_ping(ip):
    test = os.popen(pi + ip).read()
    if test.count("1 received") == 1:
        change_status(ip, "Normal")
    else:
        change_status(ip, "Error")
    try:
        time = re.findall(r".*time=(.*ms).*", test)[0]
    except Exception:
        time = "timeout"
    change_delay(ip, time)


def run_check():
    temp_list = []
    for ip in find_ip():
        temp_list.append(gevent.spawn(check_ping, ip))
    gevent.joinall(temp_list)
