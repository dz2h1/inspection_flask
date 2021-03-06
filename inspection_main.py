# Author: dz2h1
from gevent import monkey; monkey.patch_all()
import datetime

from flask import Flask, redirect, render_template, request, url_for

from config.settings import (ver, get_platform, logs_find_limit, reportSetTime,
                                schedulerEnabled, crontabTime, crondevTime)
from check_dev.disweb import find_all as find_dev_all
from check_dev.disweb import insert_dev, remove_dev
from check_info.disweb import find_info_all, insert_info, remove_info
from check_info.sshcheck import run_infocheck
from check_svr.disweb import find_all as find_svr_all
from check_svr.disweb import find_sizeall as find_size_all
from check_svr.disweb import insert_size, insert_svr, remove_size, remove_svr
from check_svr.sizecheck import run_check as run_sizecheck
from check_svr.sizecheck import update_refer
from check_svr.svrcheck import run_check as run_svrcheck
from check_port.disweb import (find_port_all, add_port, remove_port,
                                insert_port_dev, remove_port_dev)
from check_port.portcheck import run_portcheck
from logs.disweb import del_logs
from logs.disweb import find_all as find_logs_all
from logs.disweb import find_logs_num
from check_base import check_send, report_send
if get_platform() == "Windows":
    from charts.disweb_win import (del_charts, find_chart_logs_num,
                                    make_chart_db_aggr, run_charts_check)
    from check_dev.pingcheck_win import run_check as run_pingcheck
    from check_dev.pingcheck_win import update_setdelay
else:
    from charts.disweb import (del_charts, find_chart_logs_num,
                                    make_chart_db_aggr, run_charts_check)
    from check_dev.pingcheck import run_check as run_pingcheck
    from check_dev.pingcheck import update_setdelay

app = Flask(__name__)


@app.route('/dev/', methods=['GET', 'POST'])
def inspection_dev():
    ''' 访问页面首先执行ping检测，数据存入数据库，之后取出数据再进行页面渲染 '''
    try:
        ''' 用于dev页面下方新报警阈值获取 '''
        devname = request.args.get('dev_name')
        setdelay = request.args.get('new_setdelay')
        if devname.strip() != "" and setdelay.isdigit():
            update_setdelay(devname.strip(), setdelay)
            return redirect(url_for('inspection_dev'))
    except Exception:
        pass

    run_pingcheck()
    l_all = find_dev_all()

    context = {
        "db_all": l_all,
        "ver": ver,
        "web_name": "dev",
    }
    return render_template('dev.html', **context)


@app.route('/svr/', methods=['GET', 'POST'])
def inspection_svr():
    ''' 访问页面执行svr设备状态码检测，再执行size页面大小检测，后取出数据进行页面渲染 '''
    try:
        ''' 用于svr页面下方标准值获取 '''
        svrname = request.args.get('svr_name')
        refer = request.args.get('new_reference')
        if svrname.strip() != "" and refer.isdigit():
            update_refer(svrname.strip(), refer)
            return redirect(url_for('inspection_svr'))
    except Exception:
        pass

    run_svrcheck()
    run_sizecheck()
    l_all = find_svr_all()
    s_all = find_size_all()

    context = {
        "db_all": l_all,
        "db_sizeall": s_all,
        "ver": ver,
        "web_name": "svr",
    }
    return render_template('svr.html', **context)


@app.route('/logs/<int:page_num>')
def inspection_logs(page_num):
    ''' 按页码取出日志数据，显示最大数量值在settings文件中修改 '''
    logs_num = find_logs_num()
    pages = [i for i in range(1,
            logs_num//logs_find_limit + (2 if logs_num%logs_find_limit != 0 else 1))]
    pages = pages if pages != [] else [1]
    if page_num not in pages:
        return redirect(url_for('inspection_logs', page_num=1))

    l_all = find_logs_all(page_num)

    context = {
        "db_all": l_all,
        "ver": ver,
        "pages": pages,
        "page_num": page_num,
        "web_name": "logs",
    }
    return render_template('logs.html', **context)


@app.route('/charts/')
def inspection_charts():
    ''' 构建页面的chart.js图表，图表历史数量在settings文件中修改 '''

    l_all = make_chart_db_aggr()

    context = {
        "db_all": l_all,
        "ver": ver,
        "web_name": "charts",
    }
    return render_template('charts.html', **context)


@app.route('/info/', methods=['GET', 'POST'])
def inspection_info():
    ''' 用于服务器巡检 '''
    try:
        ''' info页面下方巡检按钮 '''
        info_run = request.args.get('info_check')
        if info_run == "run":
            run_infocheck()
            return redirect(url_for('inspection_info'))
    except Exception:
        pass

    l_all = find_info_all()

    context = {
        "db_all": l_all,
        "ver": ver,
        "web_name": "info",
    }
    return render_template('info.html', **context)


@app.route('/port/', methods=['GET', 'POST'])
def inspection_port():
    ''' 用于端口巡检 '''
    try:
        ''' 用于port页面下方键入值获取 '''
        para = request.args.to_dict()
        for key in list(para.keys()):
            if not para.get(key):
                del para[key]
                return redirect(url_for('inspection_port'))
        if 'dev_name' in para and 'dev_port' in para:
            dev_name = para['dev_name'].strip()
            dev_port = para['dev_port']
            if dev_name != "" and dev_port != "":
                dev_port_many = []
                dev_port_many = dev_port.split()
                add_port(dev_name, dev_port_many)
                return redirect(url_for('inspection_port'))
        if 'dev_name_del' in para and 'dev_port_del' in para:
            dev_name_del = para['dev_name_del'].strip()
            dev_port_del = para['dev_port_del']
            if dev_name_del != "" and dev_port_del != "":
                dev_port_del_many = []
                dev_port_del_many = dev_port_del.split()
                remove_port(dev_name_del, dev_port_del_many)
                return redirect(url_for('inspection_port'))
    except Exception:
        pass

    run_portcheck()
    l_all = find_port_all()

    context = {
        "db_all": l_all,
        "ver": ver,
        "web_name": "port",
    }
    return render_template('port.html', **context)


@app.route('/crontab/')
def inspection_crontab():
    ''' 访问页面时执行巡检脚本 '''
    run_pingcheck()
    run_svrcheck()
    run_sizecheck()
    check_send()
    MS_time_hm = datetime.datetime.now().strftime('%H%M')
    if MS_time_hm == reportSetTime:
        report_send()
    return '<html>crontab</html>'


@app.route('/crondev/')
def inspection_crondev():
    ''' 访问页面时执行dev设备的检测并记录数据，数据用于构建charts页面折线图 '''
    run_charts_check()
    return '<html>crondev</html>'


@app.route('/console/', methods=['GET', 'POST'])
def inspection_console():
    ''' 后台获取各项输入数据，判断的上下位置顺序就是后台页面里的位置顺序，此处待优化 '''
    logs_num = find_logs_num()
    charts_num = find_chart_logs_num()

    try:
        para = request.args.to_dict()
        for key in list(para.keys()):
            if not para.get(key):
                del para[key]
                return redirect(url_for('inspection_console'))

        if 'logs_del_keepnum' in para:
            del_logs(logs_num, int(para['logs_del_keepnum'].strip()))
            return redirect(url_for('inspection_console'))

        if 'charts_del_keepnum' in para:
            del_charts(charts_num, int(para['charts_del_keepnum'].strip()))
            return redirect(url_for('inspection_console'))

        if 'dev_name' in para and 'dev_add' in para:
            insert_dev(para['dev_name'].strip(), para['dev_add'].strip())
            return redirect(url_for('inspection_console'))

        if 'svr_name' in para and 'svr_add' in para:
            insert_svr(para['svr_name'].strip(), para['svr_add'].strip())
            return redirect(url_for('inspection_console'))

        if 'size_name' in para and 'size_add' in para:
            insert_size(para['size_name'].strip(), para['size_add'].strip())
            return redirect(url_for('inspection_console'))

        if 'dev_name_port' in para and 'dev_add_port' in para \
                                   and 'dev_port_num' in para:
            insert_port_dev(para['dev_name_port'].strip(),
                            para['dev_add_port'].strip(),
                            int(para['dev_port_num'].strip()))
            return redirect(url_for('inspection_console'))

        if 'info_name' in para and 'info_add' in para \
                               and 'info_usr' in para \
                               and 'info_pw' in para \
                               and 'info_port' in para:
            insert_info(para['info_name'].strip(), para['info_add'].strip(),
                        para['info_usr'].strip(), para['info_pw'].strip(),
                        int(para['info_port'].strip()))
            return redirect(url_for('inspection_console'))

        if 'dev_del' in para:
            remove_dev(para['dev_del'].strip())
            return redirect(url_for('inspection_console'))

        if 'svr_del' in para:
            remove_svr(para['svr_del'].strip())
            return redirect(url_for('inspection_console'))

        if 'size_del' in para:
            remove_size(para['size_del'].strip())
            return redirect(url_for('inspection_console'))

        if 'dev_del_port' in para:
            remove_port_dev(para['dev_del_port'].strip())
            return redirect(url_for('inspection_console'))

        if 'info_del' in para:
            remove_info(para['info_del'].strip())
            return redirect(url_for('inspection_console'))

    except Exception as e:
        return e

    context = {
        "logs_num": logs_num,
        "charts_num": charts_num,
        "ver": ver,
        "web_name": "console",
    }
    return render_template('console.html', **context)


@app.route('/')
def inspection_root():
    ''' 访问根地址直接跳转到dev页面 '''
    return redirect(url_for('inspection_dev'))


@app.route('/logs/')
def inspection_logs_root():
    ''' 访问logs地址直接跳转到logs页面 '''
    return redirect(url_for('inspection_logs', page_num=1))


if __name__ == '__main__':
    if schedulerEnabled:
        from flask_apscheduler import APScheduler
        scheduler = APScheduler()
        scheduler.add_job(func=inspection_crontab, id='do_crontab',
                                    trigger='interval', seconds=crontabTime)
        scheduler.add_job(func=inspection_crondev, id='do_crondev',
                                    trigger='interval', seconds=crondevTime)
        scheduler.init_app(app)
        scheduler.start()
    from gevent.pywsgi import WSGIServer
    server = WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()
