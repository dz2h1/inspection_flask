# Author: dz2h1
import gevent

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


def find_dev_ips_setDelay():
    ips = []
    setDelay = []
    alls = []
    for i in coll.find({}):
        ips.append(i["address"])
        setDelay.append(i["setdelay"])
    alls = zip(ips, setDelay)
    return alls


def update_setdelay(devname, setdelay):
    try:
        nm = str(devname)
        sd = int(setdelay)
        coll.update_one({"name": nm}, {"$set": {"setdelay": sd}})
    except Exception:
        pass


def change_status(ip, sta):
    coll.update_one({"address": ip}, {"$set": {"status": sta}})


def change_delay(ip, delay):
    coll.update_one({"address": ip}, {"$set": {"delay": delay}})


def change_status_delay(ip, status, delay):
    coll.update_one({"address": ip}, {"$set": {
        "status": status,
        "delay": delay
        }})


def check_ping(ip, setDelay):

    stdout = os.popen(pi + ip).read()

    try:
        delay = re.findall(r".*time=(.*) ms.*", stdout)[0]
        if stdout.count("1 received") == 1 and float(delay) < float(setDelay):
            change_status_delay(ip, "Normal", delay)
        else:
            change_status_delay(ip, "Error", delay)
    except Exception:
        delay = "timeout"
        change_status_delay(ip, "Error", delay)


def run_check():
    temp_list = []
    for ip, setDelay in find_dev_ips_setDelay():
        temp_list.append(gevent.spawn(check_ping, ip, setDelay))
    gevent.joinall(temp_list)
