# -*- coding: utf-8 -*-


import json
from log import logs

def chkmsg(msg):
    if not isinstance(msg, dict):
        try:
            msg = msg.replace('\n', u'万恶分隔符')
            msg = json.loads(msg)
            msg['value'] = msg['value'].replace(u'万恶分隔符', '\n')
        except Exception as e:
            return Exception('error msg format')
    if isinstance(msg, dict):
        pass
    else:
        return Exception('error msg format')
    if len(msg) < 7:
        logs.info('kafka msg is not correct format')
        return Exception('error msg format')
    else:
        for i in ['host', 'trigger', 'time', 'level', 'value', 'status',
                  'eventid', 'from']:
            if i not in msg.keys():
                logs.info('kafka msg is not correct format')
                msg = Exception('error msg format')
        return msg