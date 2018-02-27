 # -*- coding: utf-8 -*-

from storage import *
from threading import Thread
from util.chkMsg import chkmsg
from util.MySQLClient import conn_db_obj
from util.kafkaAlertClient import KafkaAlertClient
from util.log import logs
from lock.source import *


class MonitorConfig(Thread):
    def __init__(self):
        super(MonitorConfig, self).__init__()

    def run(self):
        kafka_client = KafkaAlertClient()
        consumer = kafka_client.connect(default=False)
        logs.info('connect kafka config topic success')
        for msg in consumer:
            status_queue.put(msg.value)
            consumer.commit()
            logs.info('receive config topic')


class ReceiveAlerts(Thread):
    def __init__(self):
        super(ReceiveAlerts, self).__init__()
        self.dbobj = self.__connect()

    def __connect(self):
        dbob = conn_db_obj()
        return dbob

    def chk_insert(self, msg):
        msg = chkmsg(msg)
        if isinstance(msg, dict):
            # 入库
            sql = '''insert into t_msg (f_host, f_trigger, f_time, f_level, f_value, f_status, f_eventid, f_from) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s") ''' % (
                msg['host'], msg['trigger'], msg['time'], msg['level'],
                msg['value'], msg['status'], msg['eventid'], msg['from'])
            try:
                self.dbobj.mysql_insert(sql)
                sql = '''select f_id from t_msg order by f_id desc limit 1 '''
                msgid = self.dbobj.mysql_query(sql, string=True)
                msg['msg_id'] = msgid
            except Exception:
                logs.info('insert error...')
                return Exception('insert error')
        return msg

    def run(self):
        kafka_client = KafkaAlertClient()
        consumer = kafka_client.connect()
        logs.info('connect kafka alerts topic success')
        for msg in consumer:
            msg = self.chk_insert(msg.value)
            if isinstance(msg, Exception):
                if msg.message == 'insert error':
                    continue
                elif msg.message == 'error msg format':
                    consumer.commit()
                    continue
            alerts_queue.put(msg)


class Sources(dict):
    def __missing__(self, key):
        logs.error('receive error config messags %s' % key)
        return None


class ChangeConfig(Thread):
    def __init__(self):
        super(ChangeConfig, self).__init__()
        self._reload_source()

    def _reload_source(self):
        self.func = Sources()
        self.func['AllTrg'] = sys_allTrg
        self.func['ActionStragety'] = sys_action_stragety
        self.func['Cronts'] = sys_cronts
        self.func['CountMailUser'] = sys_count_mail_user
        self.func['Interval'] = sys_interval
        self.func['Rule'] = sys_rule
        self.func['User'] = sys_user

    def run(self):
        while True:
            msg = status_queue.get()
            for actions in msg['change']:
                self.func[actions]()