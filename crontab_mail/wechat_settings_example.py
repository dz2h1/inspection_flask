# Author: dz2h1
# 修改自 X-Mars/Zabbix-Alert-WeChat

import datetime
import json
import time

import requests
import urllib3

from config.settings import mongo_clinet, mongo_name, mongo_password


urllib3.disable_warnings()

clinet = mongo_clinet()
db = clinet["inspection"]
coll = db["wechat"]
db.authenticate(mongo_name(), mongo_password())

Corpid = 'XXXX--------------'  # 企业ID
Secret = 'XXXX--------------'  # 自建应用Secret
Partyid = 'X'  # 部门ID
Agentid = '100000X'  # 自建应用ID


def GetTokenFromServer():

    Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"

    Data = {"corpid": Corpid, "corpsecret": Secret}

    try:
        r = requests.get(url=Url, params=Data, verify=False)
        wechat_db = r.json()
        wechat_db['time'] = int(time.time())
    except Exception:
        return False

    if wechat_db['errcode'] != 0:
        return False
    else:
        Token = wechat_db['access_token']
        coll.find_one_and_delete({})
        coll.insert_one(wechat_db)
        return Token


def GetTokenFromDB():

    wechat_db = coll.find_one({})

    if wechat_db:

        Token_time = wechat_db['time']
        Token = wechat_db['access_token']
        Current_time = int(time.time())

    else:
        return False

    if Current_time - Token_time > 7100:
        return False

    else:
        return Token


def send_mail(Subject, Content):

    Temp_token = GetTokenFromDB()

    Token = Temp_token if Temp_token else GetTokenFromServer()

    if Token:

        Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
        Data = {
            # "touser": User,  # 企业号中的用户帐号
            # "totag": Tagid,  # 企业号中的标签id，群发使用）
            "toparty": Partyid,  # 企业号中的部门id，群发使用
            "msgtype": "text",  # 消息类型
            "agentid": Agentid,  # 企业号中的应用id
            "text": {
                "content": Subject + '\n\n' + Content
            },
            "safe": "0"
        }

        r = requests.post(url=Url, data=json.dumps(Data), verify=False)

        if r.json()['errcode'] != 0:
            return False

    else:
        return False


if __name__ == '__main__':
    '''单运行此脚本import配置文件会有路径问题，
       在from config.settings上两行
       加入import sys和sys.path.append("..")解决'''

    Subject = 'test'
    Content = datetime.datetime.now().strftime('%H:%M:%S')
    send_mail(Subject, Content)

