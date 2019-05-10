# Author: dz2h1
import gevent
from gevent import monkey; monkey.patch_all()
import requests

from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["size"]
db.authenticate(mongo_name(), mongo_password())


def find_url_refer():
    ur = []
    for i in coll.find({}):
        ur.append([i["url"], i["reference"]])
    return ur


def change_size_devi(url, size, devi):
    coll.update_one({"url": url}, {"$set": {"size": size, "deviation": devi}})


def check_size(url, refer):
    try:
        r = requests.get(url, timeout=3)
        size = len(r.text)
        devi = round(size / refer * 100, 2)
    except Exception:
        size = 0
        devi = 100
    change_size_devi(url, size, devi)


def update_refer(svrname, refer):
    try:
        nm = str(svrname)
        rf = int(refer)
        coll.update_one({"name": nm}, {"$set": {"reference": rf}})
    except Exception:
        pass


def run_check():
    temp_list = []
    for u, r in find_url_refer():
        temp_list.append(gevent.spawn(check_size, u, r))
    gevent.joinall(temp_list)

