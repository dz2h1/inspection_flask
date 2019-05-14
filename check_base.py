# Author: dz2h1
import datetime

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

MS_change = space_one.join([MS_date, MS_time, "status-change!!!"])
MS_return = space_one.join([MS_date, MS_time, "status-return"])
MS_report = space_one.join([MS_date, MS_time, "status-report"])

logs_content = []

dev_db = find_devall()
svr_db = find_svrall()
size_db = find_sizeall()


def num_error_dev():
    j = 0
    for i in dev_db:
        if i["status"] == "Error":
            k = [i["status"], i["address"], i["delay"]]
            logs_content.append(space_four.join(k))
            j += 1
    return j


def num_error_svr():
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
    return check_coll.find_one({"name": "dev"})["ErrorNum"]


def oldnum_error_svr():
    return check_coll.find_one({"name": "svr"})["ErrorNum"]


NEDev = num_error_dev()
NESvr = num_error_svr()
ONEDev = oldnum_error_dev()
ONESvr = oldnum_error_svr()


def update_error_num():
    check_coll.update_one({"name": "dev"}, {"$set": {"ErrorNum": NEDev}})
    check_coll.update_one({"name": "svr"}, {"$set": {"ErrorNum": NESvr}})


def build_dev():
    MailBody = "dev网络检测：\n"
    temp = ""
    for i in dev_db:
        temp = space_four.join([i["address"], "\n", i["status"], i["delay"], "\n"])
        MailBody += temp
    MailBody += space_sep
    return MailBody


def build_svr():
    MailBody = "svr状态码检测：\n"
    temp = ""
    for i in svr_db:
        temp = space_four.join([i["name"], "\n", i["status"], str(i["code"]), "\n"])
        MailBody += temp
    MailBody += space_sep
    return MailBody


def build_size():
    MailBody = "页面大小检测：\n"
    temp = ""
    for i in size_db:
        temp = space_four.join([
            i["name"], "\n",
            str(i["deviation"]),
            str(i["size"]),
            str(i["reference"]), "\n"
        ])
        MailBody += temp
    MailBody += space_sep
    return MailBody


def sendmail(MS):
    build_body = build_dev() + build_svr() + build_size()
    send_mail(MS, build_body)


def insert_logs(logs_date, logs_time, logs_content):
    logs_coll.insert_one({
        "date": logs_date,
        "time": logs_time,
        "content": logs_content
    })


def judge():

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
    judge()
    update_error_num()


def report_send():
    sendmail(MS_report)


if __name__ == '__main__':
    check_send()

