# -*- coding: utf-8 -*-


from util.log import logs
from storage import classify_queue
from classify import ClassifyAct


class ClassifyOPS(object):
    def __init__(self):
        super(ClassifyOPS, self).__init__()

    def start(self):
        # 消息分类
        classfiy = ClassifyAct()
        classfiy.setDaemon(True)
        classfiy.setName('classfiy')
        classfiy.start()
        logs.info('start classify process success')

    @staticmethod
    def get_msg(types='classify'):
        if types == 'classify':
            return classify_queue.get()

    @staticmethod
    def put_msg(msg, types='classify'):
        if types == 'classify':
            classify_queue.put(msg)

    @staticmethod
    def get_queue():
        return classify_queue

classifys = ClassifyOPS()