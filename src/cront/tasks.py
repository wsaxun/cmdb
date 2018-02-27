# -*- coding: utf-8 -*-
import datetime
import time
from abc import ABCMeta, abstractmethod
from util.MySQLClient import conn_db_obj
from mail.mailOPS import mail_action
from msg.receiveMsg import ReceiveAlerts
from msg.msg import msg
from util.log import logs
from util.zabbix import ZabbixApplication
from lock.source import *


class BaseTask(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self):
        pass

    def connect(self):
        dbobj = conn_db_obj()
        return dbobj



class CountMSGS(BaseTask):
    def __init__(self):
        super(CountMSGS, self).__init__()
        self.dbob = self.connect()

    def __call__(self):
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        query_years = str(yesterday.year)
        query_month = str(yesterday.month)
        if len(query_month) == 1:
            query_month = '0' + str(query_month)
        query_day = str(yesterday.day)
        if len(query_day) == 1:
            query_day = '0' + str(query_day)
        sql = ("select f_host, f_trigger, f_time from t_msg where f_time "
               "like '%s-%s-%s'  and f_status = 'PROBLEM' order by 'f_host' " % (
                   query_years, query_month, query_day + '%'))
        results = self.dbob.mysql_query(sql, string=False)
        sql = ("select m.f_host, m.f_trigger, m.f_time from t_alerts a left "
               "join t_msg m on m.f_id = a.f_msg_id order by m.f_host")
        alerts = self.dbob.mysql_query(sql, string=False)
        mail_action.put_msg(
            {'type': 'count', 'data': {'alerts': alerts, 'results': results}})


class RepeatAlert(BaseTask):
    def __init__(self):
        super(RepeatAlert, self).__init__()
        self.dbob = self.connect()

    def __call__(self):
        sql = ("select m.f_host, m.f_trigger, m.f_time, m.f_level, m.f_value, "
               "m.f_status, m.f_eventid, a.f_rule_id  from t_alerts a "
               "left join t_msg m on m.f_id = a.f_msg_id "
               "where a.f_rule_id  is not null ")
        alert_msg = self.dbob.mysql_query(sql, string=False)
        if alert_msg:
            current_time = time.time()
            interval = sys_interval.get_query_interval()[0][0]
            max_time = current_time - interval
            for i in alert_msg:
                event_time = time.mktime(i[2].timetuple())
                if event_time > max_time:
                    continue
                msgs = {'host': i[0], 'trigger': i[1], 'time': i[2].__str__(),
                        'level': i[3], 'value': i[4], 'status': i[5],
                        'eventid': i[6], 'ids': i[-1]}
                mail_action.put_msg({'type': 'repeat','data': msgs})


class RemoveAlerts(BaseTask):
    def __init__(self):
        super(RemoveAlerts, self).__init__()
        self.dbob = self.connect()
        self.f_value = u'本消息由daemon自动生成,用于定时删除已消失但zabbix未发送的OK状态的msg'
        self.f_status = u'OK'
        self.f_level = u'High'
        self.f_eventid = u'-1'
        self.f_from = u'daemon'

    def __call__(self):
        result = []
        msga = {}
        alert_list = []
        zabbix = ZabbixApplication()
        alerts = zabbix.get_alerts()
        sql = ("select m.f_host, m.f_trigger from t_alerts a "
               "left join t_msg m  on a.f_msg_id = m.f_id")
        db_alerts_list = self.dbob.mysql_query(sql, string=False)
        if not db_alerts_list:
            return True
        # 开始比较信息
        for i in db_alerts_list:
            status = True
            for n in alerts:
                host = n[u'hosts'][0][u'host']
                trigger_name = n[u'description']
                if host == i[0] and trigger_name == i[1]:
                    status = False
                    break
            if status:
                alert_list.append([i[0], i[1]])

        # 生成完整msg信息
        ''' 生成的msg信息对比从kafka取出的相对较小
            只有host， trigger， 其它字段没有或者为默认值
        '''
        if alert_list:
            for i in alert_list:
                msga['host'] = i[0]
                msga['trigger'] = i[1]
                msga['time'] = datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')
                msga['level'] = self.f_level
                msga['value'] = self.f_value
                msga['status'] = self.f_status
                msga['eventid'] = self.f_eventid
                msga['from'] = self.f_from
                result.append(msga)
                logs.info(u'%s -- %s   daemon消除' % (i[0], i[1]))
                msga = {}
        if result:
            insert_msg = ReceiveAlerts()
            for i in result:
                msgs = insert_msg.chk_insert(i)
                msg.put_msg(msgs)
