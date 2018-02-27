# -*- coding: utf-8 -*-
import os
import time
import sys
from msg.msg import msg
from classify.classifyOPS import classifys
from stragety.stragetyOPS import stragetys
from mail.mailOPS import mail_action
from cront.cront import crontab
from cache.caches import Caches
from util.daemon import create_daemon
from util.log import log_init, logs
from util.zabbix import ZabbixApplication

reload(sys)
sys.setdefaultencoding('utf-8')


def main():
    paths = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir,
                     'log/collectAlerts.log'))

    create_daemon()
    # 初始化日志
    log_init(logs, paths)

    # 进程重启时刷新应用集
    classify = ZabbixApplication()
    classify.update_trigger()

    # 启动mail模块
    mail_action.start()

    # 启动msg模块
    msg.start()

    # 启动classify模块
    classifys.start()

    # 启动邮件聚合
    stragetys.start()

    # 启动定时计划任务
    crontab.start()

    # 重载cache
    caches = Caches()
    caches.caches()
    logs.info('load cache success')

    while True:
        time.sleep(60)


if __name__ == '__main__':
    main()
