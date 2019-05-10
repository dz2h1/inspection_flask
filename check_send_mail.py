# Author: dz2h1
import datetime

from check_base import check_send
from check_dev.pingcheck import run_check as run_pingcheck
from check_svr.sizecheck import run_check as run_sizecheck
from check_svr.svrcheck import run_check as run_svrcheck
from config.settings import reportSetTime
'''
巡检脚本，用于巡检触发时候执行哪些检测
run_pingcheck()，dev设备的ping检测
run_svrcheck()，svr页面的状态码检测
run_sizecheck()，size页面的大小检测
该处默认进行size检测，可依照需求添加检测项目
'''

run_sizecheck()

check_send()  # 执行检测
'''
用于每日报告， 如在settings中设定的时间触发巡检，则执行报告检测
报告检测内项目请勿于上方巡检项目重复，如上方三项检测全做下方只进行
报告report_send()即可
'''

MS_time_hm = datetime.datetime.now().strftime('%H%M')
if MS_time_hm == reportSetTime:

    from check_base import report_send

    run_pingcheck()
    run_svrcheck()
    report_send()  # 发送报告
