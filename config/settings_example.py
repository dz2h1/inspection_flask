# Author: dz2h1
# inspection's settings
import pymongo
import platform

ver = 'V0.2.1'  # 网页右上角的版本显示
mongodb_add = '192.168.1.1'  # mongodb数据库地址
mongodb_port = 27017  # 数据库端口，默认27017
logs_find_limit = 8  # log页面最大展示条目数量
charts_dis_num_limit = 12  # chart页面每个图表数据历史数量
pageSizeChangeUpper = 105  # size页面变化正常上限，单位（%）
pageSizeChangelower = 95  # size页面变化正常下线，单位（%），超过上下限将触发报警
reportSetTime = '0830'  # 巡检邮件报告时间

'''
支持企业微信消息报警:
在check_base中取消注释from crontab_mail.wechat_settings import send_mail启用功能
并注释其上一行以取消邮件报警
'''


def mongo_clinet():
    ''' inspection数据库接口函数'''
    return pymongo.MongoClient(host=mongodb_add,
                               port=mongodb_port,
                               connect=False)


def mongo_name():
    ''' inspection数据库用户名'''
    return 'admin'


def mongo_password():
    ''' inspection数据库密码，可修改为从环境变量读取用户名密码'''
    return '123456'


def get_platform():
    '''获取运行系统类型'''
    return platform.system()
