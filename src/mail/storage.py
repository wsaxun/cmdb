# -*- coding: utf-8 -*-


import Queue

__all__ = ['mail_queue']

MAX_MAIL_NUM = 10000
mail_queue = Queue.Queue(MAX_MAIL_NUM)
