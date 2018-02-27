# -*- coding: utf-8 -*-


from alertScheduler import TaskDaemon


class Cront(object):
    def __init__(self):
        super(Cront, self).__init__()

    @staticmethod
    def start():
        """
        每日邮件汇总任务
        未解决故障定时发送
        zabbix应用集更新
        故障自动消除
        """
        task = TaskDaemon()
        task.setDaemon(True)
        task.setName('task')
        task.start()


crontab = Cront()