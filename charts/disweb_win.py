# Author: dz2h1
import datetime
import os
import re

from check_dev.pingcheck_win import find_dev_names_ips
from config.settings import (charts_dis_num_limit, mongo_clinet, mongo_name,
                             mongo_password)


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["charts"]
db.authenticate(mongo_name(), mongo_password())

pi = "ping -n 1 -w 1000 "
dis_num_limit = charts_dis_num_limit


def check_ping_delay(ip):
    '''为run_charts_check()提供delay值'''
    cmd = os.popen(pi + ip).read()
    try:
        delay = re.findall(r".*=(.*)ms TTL.*", cmd)[0]
    except Exception:
        delay = -5
    return float(delay)


def insert_charts_logs(logs_date, logs_time, name, address, delay):
    '''为run_charts_check()提供插入数据库charts功能'''
    coll.insert_one({
        "date": logs_date,
        "time": logs_time,
        "name": name,
        "address": address,
        "delay": delay
    })


def run_charts_check():
    '''为定时巡检dev设备历史使用/crondev/'''
    for name, ip in find_dev_names_ips():
        logs_date = datetime.datetime.now().strftime('%Y-%m-%d')
        logs_time = datetime.datetime.now().strftime('%H:%M:%S')
        delay = check_ping_delay(ip)
        insert_charts_logs(logs_date, logs_time, name, ip, delay)


def make_chart_db_aggr():
    '''为历史图表界面展示提供数据/charts/'''
    l_all = coll.aggregate([
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
            }, {
            '$unwind': {
                'path': '$address'
            }
            }, {
            '$unwind': {
                'path': '$name'
            }
            }
        ])
    l_all = list(l_all)
    return l_all


def find_chart_logs_num():
    '''后台界面/console/展示charts表数据数量使用'''
    return coll.count_documents({})


def del_charts(charts_num, charts_del_keepnum):
    '''后台界面/console/删除charts表数据使用'''
    if charts_del_keepnum < 0:
        charts_del_keepnum = 0

    charts_num -= charts_del_keepnum

    if charts_num < 0:
        charts_num = 0

    for _ in range(charts_num):
        coll.find_one_and_delete({})
