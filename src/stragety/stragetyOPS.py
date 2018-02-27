# -*- coding: utf-8 -*-


from util.log import logs
from lock.source import *
from stragetyContext import MsgContext
from stragety.stragetyEasy import StragetyEasy
from stragety.stragetyOrigin import StragetyOrigin
from storage import stragety_queue


class Stragety(object):
    def __init__(self):
        super(Stragety, self).__init__()

    def start(self):
        # 查询使用何种策略
        stragety = sys_action_stragety.get_query_action_stragety()
        # 邮件聚合策略线程
        msgstragety = MsgContext()
        msgstragety.set_behavior(eval(stragety[0][0])())
        msgstragety.msg_ploymerize(stragety)
        logs.info('start stragety process success')

    @staticmethod
    def get_msg(types='stragety'):
        if types == 'stragety':
            return stragety_queue.get()

    @staticmethod
    def put_msg(msg, types='stragety'):
        if types == 'stragety':
            stragety_queue.put(msg)


stragetys = Stragety()