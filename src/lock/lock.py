# -*- coding: utf-8 -*-
import threading

__all__ = ['lock_action_stragety', 'lock_allTrg', 'lock_count_mail_user',
           'lock_cronts', 'lock_interval', 'lock_rule', 'lock_user']


# 资源锁
class SourceLock(object):
    def __init__(self, name):
        self.name = name

    @staticmethod
    def get_lock():
        lock = threading.Lock()
        return lock


lock_allTrg = SourceLock('AllTrg').get_lock()
lock_action_stragety = SourceLock('ActionStragety').get_lock()
lock_cronts = SourceLock('Cronts').get_lock()
lock_count_mail_user = SourceLock('CountMailUser').get_lock()
lock_interval = SourceLock('Interval').get_lock()
lock_rule = SourceLock('Rule').get_lock()
lock_user = SourceLock('User').get_lock()
