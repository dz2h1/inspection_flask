# Author: dz2h1
import datetime
import os
import re

from check_dev.pingcheck import find_dev_names_ips
from config.settings import (charts_dis_num_limit, mongo_clinet, mongo_name,
                             mongo_password)


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["charts"]
db.authenticate(mongo_name(), mongo_password())

pi = "ping -c 1 -w 1 "
dis_num_limit = charts_dis_num_limit


def check_ping_delay(ip):
    cmd = os.popen(pi + ip).read()
    try:
        delay = re.findall(r".*time=(.*) ms.*", cmd)[0]
    except Exception:
        delay = -5
    return float(delay)


def insert_charts_logs(logs_date, logs_time, name, address, delay):
    coll.insert_one({
        "date": logs_date,
        "time": logs_time,
        "name": name,
        "address": address,
        "delay": delay
    })


def run_charts_check():
    for name, ip in find_dev_names_ips():
        logs_date = datetime.datetime.now().strftime('%Y-%m-%d')
        logs_time = datetime.datetime.now().strftime('%H:%M:%S')
        delay = check_ping_delay(ip)
        insert_charts_logs(logs_date, logs_time, name, ip, delay)


def find_chart_logs_all(name, find_limit):
    db_all = []
    for i in coll.find({"name": name}).sort("_id", -1).limit(find_limit):
        db_all.append(i)
    return db_all


def make_chart_db():
    l_name_ip = find_dev_names_ips()
    l_temp = []
    d_temp = {}
    l_all = []
    for name, ip in l_name_ip:
        l_temp = find_chart_logs_all(name, dis_num_limit)
        l_temp = l_temp if len(l_temp) == dis_num_limit else [{
            "time": '0',
            "delay": 0
        } for i in range(dis_num_limit)]
        l_temp_time = []
        l_temp_delay = []
        d_temp['name'] = name
        d_temp['address'] = ip
        for i in l_temp:
            l_temp_time.append(i["time"])
            l_temp_delay.append(i["delay"])
        d_temp["time"] = l_temp_time
        d_temp["delay"] = l_temp_delay
        l_all.append(d_temp.copy())
    return l_all


def make_chart_db_aggr():
    l_all = []
    l_temp = coll.aggregate([
        {
            '$sort': {
                '_id': -1
            }
        }, {
            '$group': {
                '_id': '$name', 
                'time': {
                    '$push': '$time'
                }, 
                'delay': {
                    '$push': '$delay'
                }, 
                'address': {
                    '$addToSet': '$address'
                }, 
                'name': {
                    '$addToSet': '$name'
                }
            }
        }, {
            '$project': {
                'address': 1, 
                'name': 1, 
                'time': {
                    '$slice': [
                        '$time', dis_num_limit
                    ]
                }, 
                'delay': {
                    '$slice': [
                        '$delay', dis_num_limit
                    ]
                }
                }
            }
        ])
    for i in l_temp:
        i["name"] = i["name"][0]
        i["address"] = i["address"][0]
        l_all.append(i.copy())
    return l_all


def find_chart_logs_num():
    return coll.find({}).count()


def del_charts(charts_num, charts_del_keepnum):

    if charts_del_keepnum < 0:
        charts_del_keepnum = 0

    charts_num -= charts_del_keepnum

    if charts_num < 0:
        charts_num = 0

    for i in range(charts_num):
        coll.find_one_and_delete({})
