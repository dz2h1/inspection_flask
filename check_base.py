# Author: dz2h1
import datetime
from pymongo import UpdateOne

from check_dev.disweb import find_all as find_devall
from check_svr.disweb import find_all as find_svrall
from check_svr.disweb import find_sizeall
from config.settings import (mongo_clinet, mongo_name, mongo_password,
                             pageSizeChangelower, pageSizeChangeUpper)
from crontab_mail.mail_settings import send_mail
# from crontab_mail.wechat_settings import send_mail

clinet = mongo_clinet()
db = clinet["inspection"]
svr_coll = db["svr"]
dev_coll = db["dev"]
check_coll = db["check"]
logs_coll = db["logs"]
size_coll = db["size"]
db.authenticate(mongo_name(), mongo_password())

MS_date = datetime.datetime.now().strftime('%Y-%m-%d')
MS_time = datetime.datetime.now().strftime('%H:%M:%S')

space_one = " "
space_four = "      "
space_sep = "-" * 40 + "\n"
content_length_dis = " B"
percent_dis = "%"
colon_dis = "："

MS_change = space_one.join([MS_date, MS_time, "status-change!!!"])
MS_return = space_one.join([MS_date, MS_time, "status-return"])
MS_report = space_one.join([MS_date, MS_time, "status-report"])

logs_content = []

dev_db = find_devall()
svr_db = find_svrall()
size_db = find_sizeall()


def num_error_dev():
    '''获取dev库中异常设备的数量'''
    j = 0
    for i in dev_db:
        if i["status"] == "Error":
            k = [i["status"], i["address"], i["delay"]]
            logs_content.append(space_four.join(k))
            j += 1
    return j


def num_error_svr():
    '''获取svr库中异常设备的数量'''
    j = 0
    for i in svr_db:
        if i["status"] == "Error":
            k = [i["status"], i["name"], str(i["code"])]
            logs_content.append(space_four.join(k))
            j += 1

    for i in size_db:
        if i["deviation"] > pageSizeChangeUpper or i[
                "deviation"] < pageSizeChangelower:
            l = [
                str(i["deviation"]), i["name"],
                str(i["size"]),
                str(i["reference"])
            ]
            logs_content.append(space_four.join(l))
            j += 1
    return j


def oldnum_error_dev():
    '''获取check库中上次检测的dev库异常设备数量'''
    return check_coll.find_one({"name": "dev"})["ErrorNum"]


def oldnum_error_svr():
    '''获取check库中上次检测的svr库异常设备数量'''
    return check_coll.find_one({"name": "svr"})["ErrorNum"]


NEDev = num_error_dev()
NESvr = num_error_svr()


try:
    '''从check库中获取异常设备数量，如果没有则初始化check库'''
    ONEDev = oldnum_error_dev()
    ONESvr = oldnum_error_svr()
except Exception:
    check_coll.insert_many([{"name": "dev", "ErrorNum": 0}, {"name": "svr", "ErrorNum": 0}])
    ONEDev = 0
    ONESvr = 0


def update_error_num():
    '''向check库更新dev和svr异常设备数量'''
    arr = [
        UpdateOne({"name": "dev"}, {"$set": {"ErrorNum": NEDev}}),
        UpdateOne({"name": "svr"}, {"$set": {"ErrorNum": NESvr}})
    ]
    check_coll.bulk_write(arr)


def build_dev():
    '''创建邮件正文，dev设备部分'''
    MailBody = "dev网络检测：\n"
    temp = ""
    for i in dev_db:
        address_dis = i["address"] + colon_dis
        temp = space_four.join([address_dis, "\n", i["status"], i["delay"], "\n"])
        MailBody += temp
    MailBody += space_sep
    return MailBody


def build_svr():
    '''创建邮件正文，svr设备部分'''
    MailBody = "svr状态码检测：\n"
    temp = ""
    for i in svr_db:
        name_dis = i["name"] + colon_dis
        temp = space_four.join([name_dis, "\n", i["status"], str(i["code"]), "\n"])
        MailBody += temp
    MailBody += space_sep
    return MailBody


def build_size():
    '''创建邮件正文，size设备部分'''
    MailBody = "页面大小检测：\n"
    temp = ""
    for i in size_db:
        name_dis = i["name"] + colon_dis
        deviation_dis = str(i["deviation"]) + percent_dis
        size_dis = str(i["size"]) + content_length_dis
        reference_dis = str(i["reference"]) + content_length_dis
        temp = space_four.join([
            name_dis, "\n",
            deviation_dis,
            size_dis,
            reference_dis, "\n"
            ])
        MailBody += temp
    MailBody += space_sep
    return MailBody


def sendmail(MS):
    '''汇总三部分设备信息，创建邮件正文并发送邮件'''
    build_body = build_dev() + build_svr() + build_size()
    send_mail(MS, build_body)


def insert_logs(logs_date, logs_time, logs_content):
    '''向log库插入信息'''
    logs_coll.insert_one({
        "date": logs_date,
        "time": logs_time,
        "content": logs_content
    })


def judge():
    '''巡检判断的核心函数，根据结果判断是否发送邮件'''
    RT = 0
    CH = 0

    if NEDev == 0:
        if NEDev != ONEDev:
            RT += 1
    elif NEDev != ONEDev:
        CH += 1

    if NESvr == 0:
        if NESvr != ONESvr:
            RT += 1
    elif NESvr != ONESvr:
        CH += 1

    if RT > 0:
        sendmail(MS_return)
        insert_logs(MS_date, MS_time, "return")

    if CH > 0:
        sendmail(MS_change)
        for i in logs_content:
            insert_logs(MS_date, MS_time, i)


def check_send():
    '''本脚本的接口函数。执行判断和向check库更新故障设备数量'''
    judge()
    update_error_num()


def report_send():
    '''定时邮件报告的函数'''
    sendmail(MS_report)


if __name__ == '__main__':
    check_send()
