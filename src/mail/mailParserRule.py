# -*- coding: utf-8 -*-
from lock.source import *


# 操作rule_id
def find_rule(msg, dbob):
    msgLevel = msg['level']
    msgTrigger = msg['trigger']
    msgHost = msg['host']
    msgApp = msg['sup_id']
    dbresult = sys_rule.get_query_rule()
    separator = '#'
    idStatus = []
    rule_id = []
    result = []
    levels = [
        'Not classified',
        'Information',
        'Warning',
        'Average',
        'High',
        'Disaster']
    # 修改栈
    for i in dbresult:
        tmp = i[1].split(separator)[1:-1]
        for k in tmp:
            if k.startswith('host'):
                tmp1 = k.split()
                if tmp1[1] == '==':
                    if msgHost == tmp1[-1]:
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
                else:
                    if msgHost != tmp1[-1]:
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
            elif k.startswith('app'):
                tmp1 = k.split()
                sql = '''select f_id from t_classification_sup where f_name like '%s' ''' % (
                '%' + tmp1[-1] + '%')
                query_sup_id = dbob.mysql_query(sql, string=False)
                if query_sup_id:
                    query_sup_id = query_sup_id[0][0]
                if tmp1[1] == '==':
                    if msgApp == query_sup_id:
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
                else:
                    if msgApp != query_sup_id:
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
            elif k.startswith('level'):
                tmp1 = k.split()
                if tmp1[1] == '==':
                    if msgLevel == tmp1[-1]:
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
                elif tmp1[1] == '!=':
                    if msgLevel != tmp1[-1]:
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
                elif tmp1[1] == '>=':
                    if levels.index(msgLevel) >= levels.index(tmp1[-1]):
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
                elif tmp1[1] == '<=':
                    if levels.index(msgLevel) >= levels.index(tmp1[-1]):
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
            elif k.startswith('trigger'):
                if k.startswith('trigger in'):
                    if k[12:] in msgTrigger:
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
                elif k.startswith('trigger not in'):
                    if k[16:] not in msgTrigger:
                        ops(idStatus, 1)
                    else:
                        ops(idStatus, 0)
            elif k == 'and' or k == 'or':
                idStatus.append(k)
            else:
                break

        if idStatus[0]:
            ids = int(i[0])
            rule_id.append(ids)
        idStatus = []

    # 优先级
    if rule_id:
        result = [rule_id[0]]
    return result


def update_alerts(ids, msg, dbob):
    # update t_alert 的f_rule_id                                            
    all_rule = []
    if ids:
        for i in ids:
            a = str(i)
            all_rule.append(a)
        ids = ','.join(all_rule)
        sql = ("update t_alerts set f_rule_id = '%s' where "
               "f_msg_id = (select f_id from t_msg where "
               "f_eventid = %s order by f_id desc limit 1)" % (
               ids, msg['eventid']))
        dbob.mysql_insert(sql)


def ops(stacks, opsStatus):
    # 通用入栈
    if not stacks:
        stacks.append(opsStatus)
    elif len(stacks) == 1:
        stacks.append(opsStatus)
    else:
        opers = stacks.pop()
        oldnum = stacks.pop()
        if opers == 'and':
            if oldnum and opsStatus:
                stacks.append(1)
            else:
                stacks.append(0)
        elif opers == 'or':
            if oldnum or opsStatus:
                stacks.append(1)
            else:
                stacks.append(0)
