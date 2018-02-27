# -*- coding: utf-8 -*-
from msg.msg import msg
from threading import Thread
from util.MySQLClient import conn_db_obj
from mail.mailOPS import mail_action
from util.log import logs
from storage import classify_queue
from lock.source import *


class classify(object):
    def __init__(self):
        super(classify, self).__init__()

    def __actions(self, msgs, dbob):
        f_host = msgs['host']
        f_trigger = msgs['trigger']
        f_status = msgs['status']
        sendnow = msgs['sub_sendnow']
        mail_status = 0
        f_sub_id = msgs['sub_id']
        # 分类入库
        if f_status == 'PROBLEM':
            msgid = msgs['msg_id']
            sql = '''insert into t_alerts (f_msg_id, f_sup_id) values (%s, %s) ''' % (
                msgid, msgs['sup_id'])
            logs.info("msg_id %s 插入 t_alerts 成功" % msgid)
            dbob.mysql_insert(sql)
            # 邮件
            if sendnow:
                mail_action.put_msg({'type': 'classify','data': msgs})
                return msgs

            sql = (
                "insert into t_msg_action (f_msg_id, f_sub_id, f_send_status) "
                "values (%s, %s, '%d')" % (
                    msgid, f_sub_id, mail_status))
            dbob.mysql_insert(sql)
        else:
            # 消除已经恢复的告警
            sql = (
                "select alerts.f_id, alerts.f_msg_id, msg.f_host, msg.f_trigger  "
                "from t_alerts alerts  left join t_msg msg "
                "on alerts.f_msg_id = msg.f_id ")
            results = dbob.mysql_query(sql, string=False)
            delrecord = []
            for i in results:
                if i[2] == f_host and i[3] == f_trigger:
                    logs.info("t_alerts 删除 msg_id %s 成功" % i[1])
                    delrecord.append(i[0])
            for i in delrecord:
                sql = '''delete from t_alerts where f_id = %s''' % i
                dbob.mysql_query(sql, string=False)
        return msgs

    def __alter_msg(self, msgs, allTrg):
        for i in allTrg:
            if i[3] in msgs['trigger']:
                msgs['sup_id'] = i[0]
                msgs['sup_name'] = i[1]
                msgs['sub_id'] = i[2]
                msgs['sub_name'] = i[3]
                msgs['sub_sendnow'] = i[4]
                break
        else:
            for i in allTrg:
                if i[1] == '未记录应用集':
                    msgs['sup_id'] = i[0]
                    msgs['sup_name'] = i[1]
                    msgs['sub_id'] = i[2]
                    msgs['sub_name'] = i[3]
                    msgs['sub_sendnow'] = i[4]
                    break
        return msgs

    def __func_act(self, msgs, dbobj, allTrg):
        # 分类
        msgs = self.__alter_msg(msgs, allTrg)
        results = self.__actions(msgs, dbobj)
        if results:
            return results

    def chg_msg(self, msgs, dbobj, allTrg):
        msgs = self.__func_act(msgs, dbobj, allTrg)
        if msgs['status'] == 'PROBLEM' and not msgs['sub_sendnow']:
            classify_queue.put(msgs)
        return True


class ClassifyAct(Thread):
    def __init__(self):
        self.dbobj = self.__connect()
        super(ClassifyAct, self).__init__()

    def __connect(self):
        dbobj = conn_db_obj()
        return dbobj

    def run(self):
        # 消息分类
        classifys = classify()
        while True:
            msgs = msg.get_msg(types='alerts')
            allTrg = sys_allTrg.get_query_allTrg()
            classifys.chg_msg(msgs, self.dbobj, allTrg)
            logs.info('classify success %s' % (str(msgs)))
