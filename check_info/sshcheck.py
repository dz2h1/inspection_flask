# Author: dz2h1
import gevent
import base64
import re
import paramiko

from config.settings import mongo_clinet, mongo_name, mongo_password


clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["info"]
db.authenticate(mongo_name(), mongo_password())


def password_decode(password):
    '''密码解码使用'''
    return base64.b64decode(password.encode()).decode()[:-6]


def find_info_ssh():
    '''为run_infocheck()提供info库设备密码、用户名、端口和地址信息'''
    pw = []
    usr = []
    po = []
    addr = []
    for i in coll.find({}):
        pw_decode = password_decode(i["password"])
        pw.append(pw_decode)
        usr.append(i["user"])
        po.append(i["port"])
        addr.append(i["address"])
    alls = zip(pw, usr, po, addr)
    return alls


def change_info_status(address, cpu, mem, disk):
    '''为check_ssh()提供数据库信息更新'''
    coll.update_one({"address": address},
                    {"$set": {
                        "cpu": cpu,
                        "mem": mem,
                        "disk": disk
                    }})


def check_ssh(password, user, port, address):
    '''info设备巡检核心函数'''
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=address, port=port,
                           username=user, password=password, timeout=10)
        std_in, std_out, std_err = ssh_client.exec_command(
            'df -h /;w;free', timeout=5)
        res, err = std_out.read(), std_err.read()
        cmd_back_b = res if res else err
        cmd_back = cmd_back_b.decode('utf-8')
        ssh_client.close()
    except Exception:
        disk = "timeout"
        cpu = "timeout"
        mem = "timeout"
        change_info_status(address, cpu, mem, disk)
        return "connect_error"

    try:
        disk = re.findall(r"  (.*)% /.*", cmd_back)[0].split()[-1]
    except Exception:
        disk = "timeout"

    try:
        cpu = re.findall(r"load average: (.*)", cmd_back)[0].replace(",", "")
    except Exception:
        cpu = "timeout"

    try:
        mem = re.findall(r"Mem:(.*)", cmd_back)[0].split()
        mem_total = int(mem[0])
        mem_used = int(mem[1])
        mem = round(mem_used / mem_total * 100, 2)
    except Exception:
        mem = "timeout"

    change_info_status(address, cpu, mem, disk)
    return "normal"


def run_infocheck():
    '''/info/页面检测巡检设备的启动函数'''
    temp_list = []
    for password, user, port, address in find_info_ssh():
        temp_list.append(gevent.spawn(check_ssh, password, user, port, address))
    gevent.joinall(temp_list)
