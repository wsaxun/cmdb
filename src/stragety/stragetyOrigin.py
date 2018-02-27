# -*- coding: utf-8 -*-
from util.MySQLClient import conn_db_obj
from stragetyInterface import Stragety
from classify.classifyOPS import classifys
from threading import Thread
from mail.mailOPS import mail_action


class StragetyOrigin(Stragety):
    def __init__(self):
        super(StragetyOrigin, self).__init__()

    def ploymerize(self, extends):
        msgt = MsgProcessOrigin(extends)
        msgt.setDaemon(True)
        msgt.setName('StragetyOrigin')
        msgt.start()


class MsgProcessOrigin(Thread):
    def __init__(self, extends):
        self.dbob = self.__connect()
        self.extends = eval(extends[0][1])
        super(MsgProcessOrigin, self).__init__()

    def __connect(self):
        dbobj = conn_db_obj()
        return dbobj

    def run(self):
        while True:
            msg = classifys.get_msg()
            mail_action.put_msg({'type': 'stragetyOrigin', 'data': msg})