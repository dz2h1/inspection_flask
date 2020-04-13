# Author: dz2h1
import gevent
import telnetlib

from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["port"]
db.authenticate(mongo_name(), mongo_password())

arr = []


def find_add_port():
    '''为run_portcheck()提供port设备地址和端口'''
    db_all = []
    l_all = coll.aggregate([{
            '$unwind': {
                'path': '$ports'
            }
            }, {
            '$project': {
                'name': 1,
                'address': 1,
                'port': '$ports.port',
                'status': '$ports.status'
            }
            }, {
            '$group': {
                '_id': None,
                'address': {
                    '$push': '$address'
                },
                'port': {
                    '$push': '$port'
                }
            }
            }, {
            '$project': {
                '_id': 0
            }
            }
            ])
    for add in l_all:
        db_all = zip(add["address"], add["port"])
    return db_all


def change_port_stat(add, port, stat):
    '''为check_code()提供更新svr库页面代码和状态更新'''
    coll.update_one({"address": add,
                     "ports": {'$elemMatch': {"port":  port}}},
                    {"$set": {"ports.$.status": stat}})


def check_stat(add, port):
    '''svr页面svr设备巡检核心函数'''
    try:
        s = telnetlib.Telnet(host=add, port=port, timeout=1)
    except Exception:
        change_port_stat(add, port, "Closed")
        return "Closed"
    s.close()
    change_port_stat(add, port, "Open")


def run_portcheck():
    '''/port/页面巡检设备端口的启动函数'''
    temp_list = []
    for add, port in find_add_port():
        temp_list.append(gevent.spawn(check_stat, add, port))
    gevent.joinall(temp_list)
