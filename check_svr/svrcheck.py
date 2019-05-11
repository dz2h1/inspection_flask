# Author: dz2h1
import gevent
from gevent import monkey; monkey.patch_all()
import requests

from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["svr"]
db.authenticate(mongo_name(), mongo_password())


def find_url():
    urls = []
    for i in coll.find({}):
        urls.append(i["url"])
    return urls


def change_code(url, code):
    coll.update_one({"url": url}, {"$set": {"code": code}})


def change_svrsta(url, sta):
    coll.update_one({"url": url}, {"$set": {"status": sta}})


def change_svr_codesta(url, code, sta):
    coll.update_one({"url": url}, {"$set": {"code": code, "status": sta}})


def check_code(url):
    try:
        code = requests.head(url, timeout=1).status_code
    except Exception:
        code = 555
    if code == 200 or code == 301 or code == 302:
        change_svr_codesta(url, code, "Normal")
    else:
        change_svr_codesta(url, code, "Error")


def run_check():
    temp_list = []
    for u in find_url():
        temp_list.append(gevent.spawn(check_code, u))
    gevent.joinall(temp_list)
