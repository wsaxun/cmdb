# -*- coding: utf-8 -*-
import MySQLdb
from parserConfig import config


class MySQLClient(object):
    def __init__(self, charset="utf8", **kwargs):
        self.charset = charset
        self.kwargs = kwargs
        self.db_object = None

    def __mysql_connect(self):
        cxn = MySQLdb.connect(charset=self.charset, **self.kwargs)
        cur = cxn.cursor()
        return cur, cxn

    def mysql_connect(func):
        def connect(self, *args, **kwargs):
            if not self.db_object:
                self.db_object = self.__mysql_connect()
            if self.db_object[1]:
                try:
                    self.db_object[1].ping()
                except Exception:
                    self.db_object = self.__mysql_connect()
            return func(self, *args, **kwargs)

        return connect

    @mysql_connect
    def mysql_query(self, query, string=True):
        self.db_object[0].execute(query)
        self.db_object[1].commit()
        data = self.db_object[0].fetchall()
        if data:
            if string:
                data = data[0][0]

        return data

    @mysql_connect
    def mysql_insert(self, sql):
        self.db_object[0].execute(sql)
        self.db_object[1].commit()

    def mysql_close(self):
        if self.db_object:
            for i in self.db_object:
                if i is not None:
                    i.close()


def conn_db_obj(dbs=None):
    if not dbs:
        dbs = {
            'user': config.cfg['mysql_user'],
            'passwd': config.cfg['mysql_passwd'],
            'host': config.cfg['mysql_host'],
            'db': config.cfg['mysql_dbname']
        }
    dbobj = MySQLClient(**dbs)
    return dbobj
