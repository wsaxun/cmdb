# -*- coding: utf-8 -*-


import datetime
from threading import Thread
from lock.source import sys_count_mail_user
from mail.mailAParse import mails, parseMsg
from mail.mailParserRule import find_rule, update_alerts
from util.MySQLClient import conn_db_obj
from util.parserConfig import config
from storage import *


class MailAction(Thread):
    def __init__(self):
        super(MailAction, self).__init__()
        self.dbobj = conn_db_obj()
        self.mail = mails()
        self.msgobj = parseMsg()

    def chck_user(self, users, types):
        if config.cfg[types]:
            return users
        else:
            result = []
            for user in users:
                if '@ipanel.cn' in user[0]:
                    result.append(user)
            return result

    def run(self):
        while True:
            msg_origin = mail_queue.get()
            msgs = msg_origin['data']
            if msg_origin['type'] == 'classify':
                ids = find_rule(msgs, self.dbobj)
                body = self.msgobj.messages(msgs)
                To = self.mail.find_user(ids)
                From = config.cfg['mail_user']
                if To:
                    try:
                        mail_status = self.mail.send(To, msgs['trigger'], body,
                                                     From)
                    except Exception:
                        mail_status = 0
                # 更新t_alerts的f_rule_id
                update_alerts(ids, msgs, self.dbobj)
                sql = (
                    "insert into t_msg_action (f_msg_id, f_sub_id, f_send_status) "
                    "values (%s, %s, '%d')" % (
                        msgs['msg_id'], msgs['sub_id'], mail_status))
                self.dbobj.mysql_insert(sql)

            if msg_origin['type'] == 'count':
                today = datetime.datetime.today()
                yesterday = today - datetime.timedelta(days=1)
                bodys = self.msgobj.count_msg(msgs['results'])
                if msgs['alerts'] and msgs['results']:
                    bodys = u'\n昨日所有故障:' + bodys + u'\n\n\n\n尚未处理的故障:' + self.msgobj.count_msg(
                        msgs['alerts'])
                elif msgs['alerts'] and not msgs['results']:
                    bodys = u'\n昨日所有故障:' + u'\n无故障' + u'\n\n\n\n尚未处理的故障:' + self.msgobj.count_msg(
                        msgs['alerts'])
                elif not msgs['alerts'] and msgs['results']:
                    bodys = u'\n昨日所有故障:' + bodys + u'\n\n\n\n尚未处理的故障:\n' + u"无故障"
                elif not msgs['alerts'] and not msgs['results']:
                    bodys = u'\n昨日所有故障:' + u'\n无故障' + u'\n\n\n\n尚未处理的故障:\n' + u"无故障"
                To = sys_count_mail_user.get_query_count_mail_user()
                To = self.chck_user(To, 'mail_enable_outside_mail_count')
                From = config.cfg['mail_user']
                self.mail.send(To, u'%s 告警邮件汇总[%d-%d-%d]' % (
                    config.cfg['mail_name'], yesterday.year,
                    yesterday.month,
                    yesterday.day), bodys, From, Mails=True, Phones=False)


            if msg_origin['type'] == 'repeat':
                tmp = []
                body = self.msgobj.messages(msgs)
                ids = msgs['ids']
                if ',' in ids:
                    ids = ids.split(',')
                    for n in ids:
                        tmp.append(int(n))
                    ids = tmp
                else:
                    ids = [int(ids)]
                subject = u'未解决故障 ' + msgs['trigger']
                From = config.cfg['mail_user']
                users = self.mail.find_user(ids)
                users = self.chck_user(users,
                                       'mail_enable_outside_mail_repeat')
                self.mail.send(users, subject, body, From, Mails=True,
                               Phones=False)

            if msg_origin['type'] == 'stragetyOrigin':
                body = self.msgobj.messages(msgs)
                subject = msgs['trigger']
                ids = find_rule(msgs, self.dbobj)
                users = self.mail.find_user(ids)
                # 更新t_alerts的f_rule_id
                update_alerts(ids, msgs, self.dbobj)
                From = config.cfg['mail_user']
                mail_status = 0

                try:
                    mail_status = self.mail.send(users, subject, body, From)
                except Exception:
                    pass
                sql = (
                    "update t_msg_action set f_send_status = '%d' "
                    "where f_msg_id = %s  " % (
                        mail_status, msgs['msg_id']))
                self.dbobj.mysql_insert(sql)

            if msg_origin['type'] == 'stragetyEasy':
                body = self.msgobj.polymt(msgs)
                ids = []
                users = ()
                for msg in msgs:
                    rule_id = find_rule(msg, self.dbobj)
                    update_alerts(rule_id, msg, self.dbobj)
                    ids += rule_id
                    users += self.mail.find_user(ids)
                # 去重
                To = set()
                for i in users:
                    To.add(i)
                if isinstance(msg_origin['classifys'], long):
                    subject = msg['sup_name'] + '告警'
                else:
                    subject = msg_origin['classifys'] + '主机告警'
                From = config.cfg['mail_user']
                try:
                    mails_status = self.mail.send(To, subject, body, From)
                except Exception:
                    pass
                for i in msgs:
                    sql = ("update t_msg_action set f_send_status = '%d'"
                           " where f_msg_id = %s  " % (
                           mails_status, i['msg_id']))
                    self.dbobj.mysql_insert(sql)