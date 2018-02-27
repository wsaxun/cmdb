# -*- coding: utf-8 -*-


from util.log import logs
from mailAction import MailAction
from storage import *

__all__ = ['mail_action']


class MailOPS(object):
    def __init__(self):
        super(MailOPS, self).__init__()

    def start(self):
        # 邮件发送
        mail_obj = MailAction()
        mail_obj.setDaemon(True)
        mail_obj.setName('mail')
        mail_obj.start()
        logs.info('start mail process success')

    def get_msg(self, types="mail"):
        if types == 'mail':
            return mail_queue.get()

    def put_msg(self, msgs, types="mail"):
        if types == 'mail':
            mail_queue.put(msgs)


mail_action = MailOPS()
