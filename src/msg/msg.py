# -*- coding: utf-8 -*-


from storage import *
from util.log import logs
from receiveMsg import MonitorConfig, ReceiveAlerts, ChangeConfig


class Msg(object):
    def __init__(self):
        super(Msg, self).__init__()

    def start(self):
        # 监测配置变更线程
        monitor_config = MonitorConfig()
        monitor_config.setDaemon(True)
        monitor_config.setName('MonitorConfig')
        monitor_config.start()
        logs.info('start MonitorConfig process success')

        # 重装配置线程
        change_config = ChangeConfig()
        change_config.setDaemon(True)
        change_config.setName('ChangeConfig')
        change_config.start()
        logs.info('start ChangeConfig process success')

        # 接受告警信息线程
        alert_msg = ReceiveAlerts()
        alert_msg.setDaemon(True)
        alert_msg.setName('ReceiveAlerts')
        alert_msg.start()
        logs.info('start ReceiveAlerts process success')

    @staticmethod
    def get_msg(types=None):
        if types == 'status':
            return status_queue.get()
        else:
            return alerts_queue.get()

    @staticmethod
    def put_msg(msgs, types=None):
        if types == 'status':
            status_queue.put(msgs)
        else:
            alerts_queue.put(msgs)


msg = Msg()