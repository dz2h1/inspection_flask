# Author: dz2h1
# inspection's settings
import pymongo
import platform

ver = 'V0.2.4'  # 网页右上角的版本显示
mongodb_add = '192.168.1.1'  # mongodb数据库地址
mongodb_port = 27017  # 数据库端口，默认27017
logs_find_limit = 30  # log页面最大展示条目数量
charts_dis_num_limit = 12  # chart页面每个图表数据历史数量
pageSizeChangeUpper = 105  # size页面变化正常上限，单位（%）
pageSizeChangelower = 95  # size页面变化正常下线，单位（%），超过上下限将触发报警
schedulerEnabled = False  # 是否启动定时巡检True/False（bool）
reportSetTime = '0830'  # 每天邮件报告时间（str）
crontabTime = 60  # 巡检间隔时间默认为秒（int），改为其他请在inspection_main中最后处修改seconds
                  # 有minutes、hours、days、weeks可选
crondevTime = 5  # charts页面数据更新间隔时间默认为秒（int），其余信息同上

'''
v0.1.2版本中支持企业微信消息报警
在check_base中选择注释from crontab_mail.XXX_settings启用功能
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
