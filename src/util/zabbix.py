# -*- coding: utf-8 -*-
import re
from urlparse import urlparse
from MySQLClient import conn_db_obj
from pyzabbix import ZabbixAPI
from parserConfig import config
from lock.lock import lock_allTrg
from lock.source import sys_allTrg


class ZabbixApplication(object):
    def __init__(self):
        self.zabbix_url = config.cfg['zabbix_zabbix_url']
        self.zabbix_user = config.cfg['zabbix_zabbix_user']
        self.zabbix_passwd = config.cfg['zabbix_zabbix_passwd']
        self.auth = None
        self.dbobj = conn_db_obj()
        super(ZabbixApplication, self).__init__()

    @property
    def zabbix_url(self):
        return self._zabbix_url

    @zabbix_url.setter
    def zabbix_url(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            url = urlparse(value)
            if not url.hostname:
                raise TypeError('invaild zabbix url')
            self._zabbix_url = value
        else:
            raise TypeError('args error, it must be a str or unicode')

    def _login(func):
        def zabbix_login(self, *args, **kwargs):
            if not self.auth:
                zabbix = ZabbixAPI(self.zabbix_url)
                zabbix.login(self.zabbix_user, self.zabbix_passwd)
                self.auth = zabbix
            result = func(self, *args, **kwargs)
            return result

        return zabbix_login

    def get_trigger_property(self, trigger_name):
        tmp = list(set(re.split('{.*}', trigger_name)))
        while u'' in tmp:
            tmp.remove(u'')

        result = u''
        for i in tmp:
            if len(i.encode('utf-8')) > len(result.encode('utf-8')):
                result = i.strip()

        return result

    @_login
    def get_host(self):
        hosts = self.auth.host.get(output='hostid', selectGroups="Homed集群")
        result = []
        if hosts:
            for i in hosts:
                result.append(i['hostid'])
            return result
        else:
            print("No hosts found")

    @_login
    def get_application(self):
        app_list = self.auth.application.get(output=['name', 'hostid',
                                                     'applicationid'],
                                             templated=True)
        result = []
        tmp = []
        if app_list:
            for i in app_list:
                if i['name'] not in tmp:
                    tmp.append(i['name'])
                    result.append((i['name'], i['applicationid']))
            return result
        else:
            print('No application list')

    @_login
    def get_trigger(self, application):
        result = {}
        for i in application:
            tmp = []
            item_list = self.auth.item.get(
                output=['itemid'],
                applicationids=i[1]
            )
            for j in item_list:
                tmp.append(j['itemid'])
            trigger_list = self.auth.trigger.get(
                output=['description'],
                itemids=tmp
            )

            def push_trigger(storage, key, trigger_name):
                if len(trigger_name) <= 4:
                    return False
                if storage.has_key(key):
                    if trigger_name not in storage[key]:
                        storage[key].append(trigger_name)
                else:
                    storage[key] = [trigger_name]

            for n in trigger_list:
                push_trigger(result, i[0],
                             self.get_trigger_property(n['description']))

            trigger_list = self.auth.triggerprototype.get(
                output=['description'],
                applicationids=i[1]
            )

            for n in trigger_list:
                push_trigger(result, i[0],
                             self.get_trigger_property(n['description']))

        return result

    @_login
    def get_alerts(self):
        alerts_list = self.auth.trigger.get(
            only_true=1,
            skipDependent=1,
            monitored=1,
            active=1,
            output=['description', 'priority'],
            expandDescription=1,
            selectHosts=['host'],
            selectItems=['lastvalue', 'lastclock'],
        )
        return alerts_list

    def get_old_trigger(self):
        result = {}
        sql = ('select p.f_name, b.f_name from t_classification_sub b left '
               'join t_classification_sup p on b.f_sup_id = p.f_id ')
        dbresult = self.dbobj.mysql_query(sql, string=False)
        if not dbresult:
            return result
        for i in dbresult:
            if result.has_key(i[0]):
                if i[1] not in result[i[0]]:
                    result[i[0]].append(i[1])
            else:
                result[i[0]] = [i[1]]
        return result

    def need_update_list(self):
        application_id = self.get_application()
        zabbix_data = self.get_trigger(application_id)
        db_data = self.get_old_trigger()
        result = {}
        tmp = []
        if not db_data:
            return zabbix_data
        for k, v in zabbix_data.items():
            if not db_data.has_key(k):
                result[k] = v
            else:
                for n in v:
                    if n not in db_data[k]:
                        tmp.append(n)
            if tmp:
                result[k] = tmp
            tmp = []
        return result

    def update_trigger(self):
        update_list = self.need_update_list()
        lock_allTrg.acquire()
        try:
            for k, v in update_list.items():
                sql = ("select f_id from t_classification_sup where"
                       " f_name = '%s'" % k)
                result = self.dbobj.mysql_query(sql, string=False)
                if not result:
                    sql = (
                        "insert into t_classification_sup (f_name, f_decription) "
                        "values ('%s', '%s') " % (
                            k.encode('utf-8'), k.encode('utf-8')))
                    sql = sql.replace('\\', '\\\\')
                    self.dbobj.mysql_insert(sql)
                    sql = ("select f_id from t_classification_sup order by"
                           " f_id desc limit 1")
                    supid = self.dbobj.mysql_query(sql, string=False)
                    for n in v:
                        sql = ("insert into t_classification_sub (f_name, "
                               "f_sup_id, f_sendnow, f_decription) values "
                               "('%s' ,%d, %d, '%s')" % (
                                   n.encode('utf-8'), int(supid[0][0]), 0,
                                   n.encode('utf-8')))
                        sql = sql.replace('\\', '\\\\')
                        self.dbobj.mysql_insert(sql)
                else:
                    for n in v:
                        sql = ("insert into t_classification_sub "
                               "(f_name, f_sup_id, f_sendnow, f_decription) "
                               "values ('%s', %d, %d, '%s') " % (
                                   n.encode('utf-8'), int(result[0][0]), 0,
                                   n.encode('utf-8')))
                        sql = sql.replace('\\', '\\\\')
                        self.dbobj.mysql_insert(sql)
            return True
        except Exception:
            return False
        finally:
            lock_allTrg.release()
            sys_allTrg()

    def __call__(self):
        self.update_trigger()
