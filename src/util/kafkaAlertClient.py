# -*- coding: utf-8 -*-
import json
from parserConfig import config
from kafka import KafkaConsumer
from kafka import SimpleClient

class KafkaAlertClient(object):
    def __init__(self):
        self.host = config.cfg['kafka_host']
        self.port = config.cfg['kafka_port']
        self.topic = config.cfg['kafka_topic']
        self.group_id = config.cfg['kafka_group_id']
        self.style = config.cfg['kafka_style']
        self._config_topic = config.cfg['kafka_conftopic']
        self.__chk_topic()

    def connect(self, default=True):
        bootstrap_servers = [self.host+':'+self.port]
        def value_deserializer(m): return json.loads(
            m.decode('utf8'))
        if default:
            consumer = KafkaConsumer(self.topic,
                                     bootstrap_servers=bootstrap_servers,
                                     auto_offset_reset=self.style,
                                     group_id=self.group_id)           
        else:
            consumer = KafkaConsumer(self._config_topic,
                                     bootstrap_servers=bootstrap_servers,
                                     value_deserializer=value_deserializer,
                                     auto_offset_reset=self.style,
                                     group_id=self.group_id)           
        return consumer

    def __chk_topic(self):
        client = SimpleClient(self.host+':'+self.port)
        client.ensure_topic_exists(self.topic)
        client.ensure_topic_exists(self._config_topic)
        client.close()

