# -*- coding: utf-8 -*-


import Queue

__all__ = ['classify_queue']


MAX_CLASSIFY_NUM = 10000
classify_queue = Queue.Queue(MAX_CLASSIFY_NUM)
