import sys
sys.path.append("..")
from config.settings import mongo_clinet, mongo_name, mongo_password
from check_dev.pingcheck import find_ip

clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["dev"]
db.authenticate(mongo_name(), mongo_password())

def setDelayNewNum():
    ''' 用于旧版本升级到v0.1.4版本dev新字段插入 '''
    for ip in find_ip():
        coll.update_one({"address": ip}, {"$set": {"setdelay": "100"}})

setDelayNewNum()
