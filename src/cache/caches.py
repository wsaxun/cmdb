# -*- coding: utf-8 -*-

from util.MySQLClient import conn_db_obj
from lock.source import sys_allTrg
from util.zabbix import ZabbixApplication
from msg.msg import msg
from stragety.stragetyOPS import stragetys


class Caches(object):
    def __init__(self):
        self.dbobj = self.__connect()
        self.allTrg = sys_allTrg.get_query_allTrg()
        self.current_alert_list = self._get_current_alert()

    def __connect(self):
        dbobj = conn_db_obj()
        return dbobj

    def _get_current_alert(self):
        zabbix = ZabbixApplication()
        alerts = zabbix.get_alerts()
        return alerts

    def classify_cache(self):
        tmp1 = []
        tmp2 = []
        tmp3 = []
        ids = []
        sql = '''select f_id from t_msg where f_status = 'PROBLEM' '''
        msg_ids = self.dbobj.mysql_query(sql, string=False)
        sql = '''select f_msg_id from t_msg_action'''
        msg_action_ids = self.dbobj.mysql_query(sql, string=False)
        for i in msg_ids:
            tmp1.append(i[0])
        for i in msg_action_ids:
            tmp2.append(i[0])

        # ok状态
        sql = '''select max(f_msg_id) from t_alerts'''
        maxid = self.dbobj.mysql_query(sql, string=False)
        if maxid and maxid[0][0] is not None:
            maxid = maxid[0][0]
            sql = '''select f_id from t_msg where (f_id > %d and f_status = 'OK') ''' % maxid
            ids = self.dbobj.mysql_query(sql, string=False)
        for i in ids:
            tmp3.append(i[0])

        # 求差集 
        classify_ids = list(set(tmp1) ^ set(tmp2))
        classify_ids = classify_ids + tmp3
        for ids in classify_ids:
            sql = '''select * from t_msg where f_id = '%s' ''' % ids
            msgs = self.dbobj.mysql_query(sql, string=False)[0]

            query_years = str(msgs[3].year)
            query_month = str(msgs[3].month)
            if len(query_month) == 1:
                query_month = '0' + str(query_month)
            query_day = str(msgs[3].day)
            if len(query_day) == 1:
                query_day = '0' + str(query_day)
            query_hour = str(msgs[3].hour)
            if len(query_hour) == 1:
                query_hour = '0' + str(query_hour)
            query_minute = str(msgs[3].minute)
            if len(query_minute) == 1:
                query_minute = '0' + str(query_minute)
            query_second = str(msgs[3].second)
            if len(query_second) == 1:
                query_second = '0' + str(query_second)

            for alert in self.current_alert_list:
                host = alert[u'hosts'][0][u'host']
                trigger_name = alert[u'description']
                event_time = '%s.%s.%s %s:%s:%s' % (
                    query_years, query_month, query_day, query_hour,
                    query_minute,
                    query_second)
                if host == msgs[1] and trigger_name == msgs[2]:
                    msga = {"host": msgs[1], "value": msgs[5],
                           "eventid": msgs[7],
                           "level": msgs[4], "from": msgs[8],
                           "trigger": msgs[2],
                           "status": msgs[6], "time": event_time,
                           'msg_id': ids}
                    msg.put_msg(msga, types='classify')
                    break

    def ploymt_cache(self):
        sql = '''select f_msg_id from t_msg_action where f_send_status = 0 '''
        msg_action_ids = self.dbobj.mysql_query(sql, string=False)
        for ids in msg_action_ids:
            ids = ids[0]
            sql = '''select * from t_msg where f_id = '%s' ''' % ids
            msgs = self.dbobj.mysql_query(sql, string=False)[0]

            query_years = str(msgs[3].year)
            query_month = str(msgs[3].month)
            if len(query_month) == 1:
                query_month = '0' + str(query_month)
            query_day = str(msgs[3].day)
            if len(query_day) == 1:
                query_day = '0' + str(query_day)
            query_hour = str(msgs[3].hour)
            if len(query_hour) == 1:
                query_hour = '0' + str(query_hour)
            query_minute = str(msgs[3].minute)
            if len(query_minute) == 1:
                query_minute = '0' + str(query_minute)
            query_second = str(msgs[3].second)
            if len(query_second) == 1:
                query_second = '0' + str(query_second)

            for alert in self.current_alert_list:
                host = alert[u'hosts'][0][u'host']
                trigger_name = alert[u'description']
                event_time = '%s.%s.%s %s:%s:%s' % (
                    query_years, query_month, query_day, query_hour,
                    query_minute,
                    query_second)
                if host == msgs[1] and trigger_name == msgs[2]:
                    msga = {"host": msgs[1], "value": msgs[5],
                           "eventid": msgs[7],
                           "level": msgs[4], "from": msgs[8],
                           "trigger": msgs[2],
                           "status": msgs[6], "time": event_time,
                           "msg_id": ids}
                    for i in self.allTrg:
                        if i[3] in msga['trigger']:
                            msga['sup_id'] = i[0]
                            msga['sup_name'] = i[1]
                            msga['sub_id'] = i[2]
                            msga['sub_name'] = i[3]
                            msga['sub_sendnow'] = i[4]
                            break
                    else:
                        for i in self.allTrg:
                            if i[1] == u'未记录应用集':
                                msga['sup_id'] = i[0]
                                msga['sup_name'] = i[1]
                                msga['sub_id'] = i[2]
                                msga['sub_name'] = i[3]
                                msga['sub_sendnow'] = i[4]
                                break

                    stragetys.put_msg(msga)
                    break

    def caches(self):
        self.classify_cache()
        self.ploymt_cache()
        self.dbobj.mysql_close()


if __name__ == '__main__':
    caches = Caches()
    caches.caches()
