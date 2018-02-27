# -*- coding: utf-8 -*-

from functools import wraps
import smtplib
import time
import urllib
import urllib2
from util.parserConfig import config
from email.mime.text import MIMEText
from util.log import logs
from util.chkMsg import chkmsg
from lock.source import *


class mails(object):
    def __init__(self):
        self.user = config.cfg['mail_user']
        self.password = config.cfg['mail_passwd']
        self.url = config.cfg['mail_url']
        self.topic = config.cfg['mail_name']
        self.smtp = config.cfg['mail_smtp']

    def retry_send(nums=3, intervals=10):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                count = 0
                while count < nums:
                    ret = func(*args, **kwargs)
                    if not isinstance(ret, Exception) and ret != int('00',
                                                                     base=2):
                        return ret
                    count += 1
                    time.sleep(intervals)
                return ret

            return wrapper

        return decorator

    @retry_send(3, 5)
    def send(self, To, Subject, messages, From, Mails=True, Phones=True):
        mailUser = []
        smsUser = []
        status = int('00', base=2)
        if not To:
            status = int('11', base=2)
            return status
        for i in To:
            if isinstance(i, unicode):
                if '@' in i:
                    mailUser.append(i)
                else:
                    smsUser.append(i)
            else:
                for n in i:
                    if '@' in n:
                        mailUser.append(n)
                    else:
                        smsUser.append(n)
        if Mails:
            if mailUser:
                mailUser = list(set(mailUser))
                Subject = '[' + self.topic + '] ' + Subject
                msg = MIMEText(messages, 'plain', 'utf-8')
                msg['Subject'] = Subject
                msg['From'] = From
                msg['To'] = ','.join(mailUser)
                msg['Accept-Language'] = 'zh-CN'
                msg['Accept-Charset'] = 'ISO-8859-1,utf-8'
                server = smtplib.SMTP(self.smtp)
                try:
                    server.login(self.user, self.password)
                    server.sendmail(From, mailUser, msg.as_string())
                    server.quit()
                    status = status | int('10', base=2)
                except Exception:
                    logs.error('send mail is failed %s' % (str(mailUser)))

        if Phones:
            if smsUser:
                smsUser = list(set(smsUser))
                messages = '[' + self.topic + '] ' + messages
                for i in smsUser:
                    values = {'pn': i, 'ct': messages, 'st': 1}
                    req = self.url + '?' + urllib.urlencode(values)
                    try:
                        urllib2.urlopen(req)
                        status = status | int('01', base=2)
                    except Exception:
                        logs.error('send phone is failed %s' % (str(smsUser)))
        return status

    def find_user(self, ids):
        # 获取发送邮件或者短信的用户联系方式
        if ids:
            all_rule = []
            if isinstance(ids, list) or isinstance(ids, tuple):
                for i in ids:
                    all_rule.append(i)
            userInfo = self.parse_user(all_rule)
            if userInfo:
                return userInfo
            else:
                return ()
        else:
            return ()

    def parse_user(self, ids):
        all_user = sys_user.get_query_user()
        user = set()
        if all_user:
            for i in all_user:
                if int(i[1]) in ids:
                    user.add(i[0])
        return tuple(user)


class parseMsg(object):
    def __init__(self):
        self.chkmsg = chkmsg

    def messages(self, msg):
        msgs = (u'告警设备: %s\n触发名称: %s\n告警时间: %s\n告警等级: '
                u'%s\n触发详情: %s\n当前状态: %s\n事件  ID: %s \n\n' % (
                msg['host'], msg['trigger'], msg['time'], msg['level'],
                msg['value'], msg['status'], msg['eventid']))
        return msgs

    def count_msg(self, msg):
        msgs = {}
        body = ''
        for i in msg:
            if not msgs.has_key(i[0]):
                tmp = u'\n告警主机: %s\n          %s     %s' % (i[0], i[2], i[1])
                msgs[i[0]] = tmp

            else:
                msgs[i[0]] = msgs[i[0]] + '\n          %s     %s' % (
                    i[2], i[1])
        for v in msgs.values():
            body = body + v
        return body

    def polymt(self, msg):
        all_msg = u' '
        if not msg:
            return None
        for msgs in msg:
            currt_msg = self.messages(msgs)
            all_msg = all_msg + currt_msg
        if all_msg == u' ':
            return None
        return all_msg
