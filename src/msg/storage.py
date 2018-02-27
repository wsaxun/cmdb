# -*- coding: utf-8 -*-


import Queue

__all__ = ['status_queue', 'alerts_queue']

MAX_STATUS_NUM = 10000
MAX_ALERTS_NUM = 10000
status_queue = Queue.Queue(MAX_STATUS_NUM)
alerts_queue = Queue.Queue(MAX_ALERTS_NUM)
