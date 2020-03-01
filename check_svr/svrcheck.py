# Author: dz2h1
import gevent
import requests

from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["svr"]
db.authenticate(mongo_name(), mongo_password())


def find_url():
    '''为run_check()提供svr设备地址'''
    urls = []
    for i in coll.find({}):
        urls.append(i["url"])
    return urls


def change_svr_codesta(url, code, sta):
    '''为check_code()提供更新svr库页面代码和状态更新'''
    coll.update_one({"url": url}, {"$set": {"code": code, "status": sta}})


def check_code(url):
    '''svr页面svr设备巡检核心函数'''
    try:
        code = requests.head(url, timeout=1).status_code
    except Exception:
        code = 555
    if code == 200 or code == 301 or code == 302:
        change_svr_codesta(url, code, "Normal")
    else:
        change_svr_codesta(url, code, "Error")


def run_check():
    '''/svr/页面巡检svr设备的启动函数'''
    temp_list = []
    for u in find_url():
        temp_list.append(gevent.spawn(check_code, u))
    gevent.joinall(temp_list)
