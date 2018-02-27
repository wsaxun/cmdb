# -*- coding: utf-8 -*-


class MsgContext(object):
    def __init__(self):
        super(MsgContext, self).__init__()

    def set_behavior(self, stragety):
        self.stragety = stragety

    def msg_ploymerize(self, extends):
        msg = self.stragety.ploymerize(extends)
        return msg