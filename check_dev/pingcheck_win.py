# Author: dz2h1
import gevent

import os
import re

from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["dev"]
db.authenticate(mongo_name(), mongo_password())
pi = "ping -4 -n 1 -w 1000 "


def find_dev_names_ips():
    '''为charts\disweb中run_charts_check()提供dev设备的name和ip'''
    names = []
    ips = []
    alls = []
    for i in coll.find({}):
        names.append(i["name"])
        ips.append(i["address"])
    alls = zip(names, ips)
    return alls


def find_dev_ips_setDelay():
    '''为run_check()提供dev设备的ip和延迟阈值'''
    ips = []
    setDelay = []
    alls = []
    for i in coll.find({}):
        ips.append(i["address"])
        setDelay.append(i["setdelay"])
    alls = zip(ips, setDelay)
    return alls


def update_setdelay(devname, setdelay):
    '''为/dev/页面提供延迟阈值入dev库使用'''
    try:
        nm = str(devname)
        sd = str(setdelay)
        coll.update_one({"name": nm}, {"$set": {"setdelay": sd}})
    except Exception:
        pass


def change_status_delay(ip, status, delay):
    '''为check_ping()更新dev设备状态和延迟使用'''
    coll.update_one({"address": ip}, {"$set": {
        "status": status,
        "delay": delay
        }})


def check_ping(ip, setDelay):
    '''检测dev设备状态的核心函数'''
    stdout = os.popen(pi + ip).read()
    
    try:
        delay = re.findall(r".*=(.*)ms TTL.*", stdout)[0]
        if stdout.count("ms") == 4 and (float(delay) < float(setDelay) 
            or str(setDelay) == "0"):
            change_status_delay(ip, "Normal", delay)
        else:
            change_status_delay(ip, "Error", delay)
    except Exception:
        delay = "timeout"
        change_status_delay(ip, "Error", delay)


def run_check():
    '''inspection_main和check_send_mail中检测dev设备状态的启动函数'''
    temp_list = []
    for ip, setDelay in find_dev_ips_setDelay():
        temp_list.append(gevent.spawn(check_ping, ip, setDelay))
    gevent.joinall(temp_list)
