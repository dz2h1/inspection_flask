# Author: dz2h1
from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["port"]
db.authenticate(mongo_name(), mongo_password())


def find_port_all():
    '''为inspection_main和check_base提供查找port库所有数据使用'''
    find_port_all_del_blank()
    l_all = coll.aggregate([
        {
            '$unwind': {
                'path': '$ports'
            }
            }, {
            '$project': {
                '_id': 0,
                'name': 1,
                'address': 1,
                'port': '$ports.port',
                'status': '$ports.status'
            }
        }
    ])
    l_all = list(l_all)
    return l_all


def find_port_all_del_blank():
    '''在def find_port_all()函数内先检测port集合内空ports项，并删除该条数据'''
    for i in coll.find({}):
        if i['ports'] == []:
            remove_port_dev(i['name'])


def add_port(dev_name, dev_port):
    '''/port/页面添加多个端口使用'''
    for i in dev_port:
        port = int(i)
        try:
            coll.update_one({"name": dev_name},
                            {"$push": {"ports": {"port": port, "status": "Closed"}}})
        except Exception:
            pass


def remove_port(dev_name, dev_port):
    '''/port/页面删除多个端口使用'''
    for i in dev_port:
        port = int(i)
        try:
            coll.update_one({"name": dev_name},
                            {"$pull": {"ports": {"port": port}}})
        except Exception:
            pass


def insert_port_dev(dev_name, dev_add, dev_port):
    '''后台/console/插入port设备使用'''
    coll.insert_one({"name": dev_name, "address": dev_add,
                    "ports": [{"port": dev_port, "status": "Error"}]})


def remove_port_dev(dev_name):
    '''后台/console/删除port设备使用'''
    coll.remove({"name": dev_name})
