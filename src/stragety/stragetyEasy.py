# -*- coding: utf-8 -*-
import time
from util.MySQLClient import conn_db_obj
from stragetyInterface import Stragety
from classify.classifyOPS import classifys
from threading import Thread
from mail.mailOPS import mail_action


class StragetyEasy(Stragety):
    def __init__(self):
        super(StragetyEasy, self).__init__()

    def ploymerize(self, extends):
        msgt = MsgProcessEasy(extends)
        msgt.setDaemon(True)
        msgt.setName('StragetyEasy')
        msgt.start()


class MsgProcessEasy(Thread):
    def __init__(self, extends):
        self.dbob = self.__connect()
        self.extends = eval(extends[0][1])
        super(MsgProcessEasy, self).__init__()

    def __connect(self):
        dbob = conn_db_obj()
        return dbob

    def run(self):
        interval = int(self.extends['interval'])
        while True:
            while True:
                polymt = self.__ploymt()
                for classifys, msgs in polymt.items():
                    mail_action.put_msg({'type': 'stragetyEasy', 'data': msgs, 'classifys': classifys})
                break
            time.sleep(interval)

    def __ploymt(self):
        classify = self.extends['classify']
        qsize = classifys.get_queue().qsize()
        polymerization = {}
        for i in range(qsize):
            try:
                msg = classifys.get_queue().get_nowait()
            except Exception:
                return {}
            if not polymerization:
                polymerization[msg[classify]] = [msg]
            else:
                if msg[classify] in polymerization.keys():
                    polymerization[msg[classify]].append(msg)
                else:
                    polymerization[msg[classify]] = [msg]
        return polymerization
