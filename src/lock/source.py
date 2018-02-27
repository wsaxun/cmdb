# -*- coding: utf-8 -*-
from util.MySQLClient import conn_db_obj
from functools import wraps
from lock import *

__all__ = ['sys_allTrg', 'sys_action_stragety', 'sys_cronts',
           'sys_count_mail_user', 'sys_interval', 'sys_rule', 'sys_user']


def singleton(cls, *args, **kwargs):
    instances = {}

    @wraps(cls)
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


def source_lock(locks):
    def decorater(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            locks.acquire()
            try:
                result = func(*args, **kwargs)
            finally:
                locks.release()
            return result

        return wrapper

    return decorater


@singleton
class AllTrg(object):
    def __init__(self):
        self.dbob = conn_db_obj()
        self.query_allTrg = self.__query_allTrg(self.dbob)

    def __query_allTrg(self, dbob):
        sql = ("select sup.f_id, sup.f_name, sub.f_id, sub.f_name, sub.f_sendnow "
               "from t_classification_sub sub left join "
               "t_classification_sup sup on sup.f_id = sub.f_sup_id  ")
        allTrg = dbob.mysql_query(sql, string=False)
        return allTrg

    @source_lock(lock_allTrg)
    def get_query_allTrg(self):
        query_allTrg = self.query_allTrg
        return query_allTrg

    def reload_query_allTrg(self):
        self.query_allTrg = self.__query_allTrg(self.dbob)

    @source_lock(lock_allTrg)
    def __call__(self):
        self.reload_query_allTrg()


@singleton
class ActionStragety(object):
    def __init__(self):
        self.dbob = conn_db_obj()
        self.query_action_stragety = self.__query_action_stragety(self.dbob)

    def __query_action_stragety(self, dbob):
        sql = '''select f_stragety,f_extend from t_stragety where f_status = 1 '''
        action_stragety = dbob.mysql_query(sql, string=False)
        return action_stragety

    @source_lock(lock_action_stragety)
    def get_query_action_stragety(self):
        query_action_stragety = self.query_action_stragety
        return query_action_stragety

    def reload_query_action_stragety(self):
        self.query_action_stragety = self.__query_action_stragety(self.dbob)

    @source_lock(lock_action_stragety)
    def __call__(self):
        self.reload_query_action_stragety()


@singleton
class Cronts(object):
    def __init__(self):
        self.dbob = conn_db_obj()
        self.query_cronts = self.__query_cronts(self.dbob)

    def __query_cronts(self, dbob):
        sql = '''select f_hour, f_minute from t_cront '''
        cronts = dbob.mysql_query(sql, string=False)
        return cronts

    @source_lock(lock_cronts)
    def get_query_cronts(self):
        query_cronts = self.query_cronts
        return query_cronts

    def reload_query_cronts(self):
        self.query_cronts = self.__query_cronts(self.dbob)

    @source_lock(lock_cronts)
    def __call__(self):
        self.reload_query_cronts()


@singleton
class CountMailUser(object):
    def __init__(self):
        self.dbob = conn_db_obj()
        self.query_count_mail_user = self.__query_count_mail_user(self.dbob)

    def __query_count_mail_user(self, dbob):
        mobile_user = []
        mail_user = []
        sql = '''select f_mail_member from t_user_group where f_mail_member !=  '' '''
        mailids = dbob.mysql_query(sql, string=False)
        result = []
        if mailids:
            sums = []
            for sid in mailids:
                tmp = sid[0].split(';')
                sums += tmp
            sums = tuple(sums)
            ids = ', '.join(sums)
            sql = '''select f_mail from t_user where f_id in (%s) ''' % (ids)
            mail_user = dbob.mysql_query(sql, string=False)
            mail_user = list(mail_user)
        sql = '''select f_mobile_member from t_user_group where f_mobile_member != '' '''
        mobileids = dbob.mysql_query(sql, string=False)
        if mobileids:
            sums = []
            for sid in mobileids:
                tmp = sid[0].split(';')
                sums += tmp
            sums = tuple(sums)
            ids = ', '.join(sums)
            sql = '''select f_mobile from t_user where f_id in (%s) ''' % (ids)
            mobile_user = dbob.mysql_query(sql, string=False)
            mobile_user = list(mobile_user)
        user = mobile_user + mail_user
        for i in user:
            if i[0] is not None and i[0] != '':
                result.append(i)
        return tuple(result)

    @source_lock(lock_count_mail_user)
    def get_query_count_mail_user(self):
        query_count_mail_user = self.query_count_mail_user
        return query_count_mail_user

    def reload_query_count_mail_user(self):
        self.query_count_mail_user = self.__query_count_mail_user(self.dbob)

    @source_lock(lock_count_mail_user)
    def __call__(self):
        self.reload_query_count_mail_user()


@singleton
class Interval(object):
    def __init__(self):
        self.dbob = conn_db_obj()
        self.query_interval = self.__query_interval(self.dbob)

    def __query_interval(self, dbob):
        sql = '''select f_interval from t_interval '''
        intervals = dbob.mysql_query(sql, string=False)
        return intervals

    @source_lock(lock_interval)
    def get_query_interval(self):
        query_interval = self.query_interval
        return query_interval

    def reload_query_interval(self):
        self.query_interval = self.__query_interval(self.dbob)

    @source_lock(lock_interval)
    def __call__(self):
        self.reload_query_interval()


@singleton
class Rule(object):
    def __init__(self):
        self.dbob = conn_db_obj()
        self.query_rule = self.__query_rule(self.dbob)

    def __query_rule(self, dbob):
        sql = ("select distinct r.f_id, r.f_rule from t_rule r left join "
               "t_action a on a.f_rule_id = r.f_id where r.f_status = 1 "
               "and r.f_priority is not NULL order by r.f_priority")
        dbresult = dbob.mysql_query(sql, string=False)
        return dbresult

    @source_lock(lock_rule)
    def get_query_rule(self):
        query_rule = self.query_rule
        return query_rule

    def reload_query_rule(self):
        self.query_rule = self.__query_rule(self.dbob)

    @source_lock(lock_rule)
    def __call__(self):
        self.reload_query_rule()


@singleton
class User(object):
    def __init__(self):
        self.dbob = conn_db_obj()
        self.query_user = self.__query_user(self.dbob)

    def __query_user(self, dbob):
        sql = '''select f_user_group_id, f_rule_id from t_action  '''
        dbresult1 = dbob.mysql_query(sql, string=False)
        all_mail = []
        all_mobile = []
        all_user = []
        result = []
        for i in dbresult1:
            sql = '''select f_mail_member, f_mobile_member from t_user_group where f_id = '%d' ''' % (
                i[0])
            tmp = dbob.mysql_query(sql, string=False)
            for n in tmp:
                if n[0] is not None and n[0] != '':
                    mails = n[0].split(';')
                    mails = ', '.join(mails)
                    sql = '''select f_mail from t_user where f_id in (%s) ''' % (
                        mails)
                    tmp1 = dbob.mysql_query(sql, string=False)
                    all_mail = list(tmp1)

                if n[1] is not None and n[1] != '':
                    mobiles = n[1].split(';')
                    mobiles = ', '.join(mobiles)
                    sql = '''select f_mobile from t_user where f_id in (%s) ''' % (
                        mobiles)
                    tmp1 = dbob.mysql_query(sql, string=False)
                    all_mobile = list(tmp1)

                mail_mobile = all_mail + all_mobile
                all_user.append({'user': mail_mobile, 'rule': i[1]})
        for i in all_user:
            for n in i['user']:
                rule = i['rule']
                user = n[0]
                if user is not None and user != '':
                    result.append((user, rule))

        return tuple(result)

    @source_lock(lock_user)
    def get_query_user(self):
        query_user = self.query_user
        return query_user

    def reload_query_user(self):
        self.query_user = self.__query_user(self.dbob)

    @source_lock(lock_user)
    def __call__(self):
        self.reload_query_user()


sys_allTrg = AllTrg()
sys_action_stragety = ActionStragety()
sys_cronts = Cronts()
sys_count_mail_user = CountMailUser()
sys_interval = Interval()
sys_rule = Rule()
sys_user = User()

if __name__ == '__main__':
    sys_allTrg = AllTrg()
    sys_allTrg.get_query_allTrg()
    sys_allTrg()
