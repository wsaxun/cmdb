# -*- coding: utf-8 -*-
import time
from functools import wraps
from threading import Thread
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from util.log import logs
from lock.source import *
from tasks import CountMSGS, RepeatAlert, RemoveAlerts, ZabbixApplication


class BaseScheduler(object):
    def __init__(self):
        self.sched = BackgroundScheduler(executors={
            'default': ThreadPoolExecutor(5),
            'processpool': ProcessPoolExecutor(4)
        })


class AlertScheduler(BaseScheduler):
    def __init__(self):
        super(AlertScheduler, self).__init__()
        self.jobs = []

    def check_args(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = args[1]
            if not isinstance(params, dict):
                raise Exception('args must be a dict')
            else:
                if not params.has_key('task'):
                    raise Exception("dict have not key 'task' ")
                else:
                    if not params.has_key('interval'):
                        if params.has_key('hour') and params.has_key('minute'):
                            pass
                        else:
                            raise Exception(
                                "dict have not key 'hour' and 'minute' ")
            result = func(*args, **kwargs)
            return result

        return wrapper

    @check_args
    def add_job(self, jobs):
        self.jobs.append(jobs)

    def get_jobs(self):
        result = self.sched.get_jobs()
        return result

    def modify(self, jobs):
        task = self.get_jobs()
        for job in task:
            if job.id in [i['task'].__name__ for i in jobs]:
                for n in jobs:
                    if n.has_key('interval'):
                        self.sched.reschedule_job(job.id, trigger='interval',
                                                  seconds=n['interval'])
                        break
                    elif n.has_key('cron'):
                        self.sched.reschedule_job(job.id, trigger='cron',
                                                  hour=n['hour'],
                                                  minute=n['minute'])
                        break

    def start(self):
        if not self.jobs:
            raise Exception('Null task')
        for job in self.jobs:
            task = job['task']()
            if job.has_key('interval'):
                self.sched.add_job(task, trigger='interval',
                                   seconds=job['interval'],
                                   id=job['task'].__name__)
            else:
                self.sched.add_job(task, trigger='cron', hour=job['hour'],
                                   minute=job['minute'],
                                   id=job['task'].__name__)
            logs.info('Add task success, task name: %s' % job[
                'task'].__class__.__name__)
        self.sched.start()


class TaskDaemon(Thread):
    def __init__(self):
        super(TaskDaemon, self).__init__()

    def run(self):
        cronts = sys_cronts.get_query_cronts()
        interval = sys_interval.get_query_interval()[0][0]
        task = AlertScheduler()
        task.add_job({'task': RepeatAlert, 'interval': interval})
        task.add_job({'task': CountMSGS, 'hour': int(cronts[0][0]),
                      'minute': int(cronts[0][1])})
        task.add_job({'task': RemoveAlerts, 'interval': 60 * 60})
        task.add_job({'task': ZabbixApplication, 'hour': 0, 'minute': 1})
        task.start()
        logs.info('start cront_mail process success')
        logs.info('start repeatalert process success')
        logs.info('start removeAlerts process success')
        logs.info('start updateZabbixApplication process success')
        cronts1 = cronts[0][0]
        cronts2 = cronts[0][1]
        while True:
            time.sleep(10)
            now_cronts = sys_cronts.get_query_cronts()
            now_interval = sys_interval.get_query_interval()[0][0]
            jobs_list = []
            if now_cronts[0][0] != cronts1 or now_cronts[0][1] != cronts2:
                jobs_list.append(
                    {'task': CountMSGS, 'hour': int(now_cronts[0][0]),
                     'minute': int(now_cronts[0][1])})
                cronts1 = now_cronts[0][0]
                cronts2 = now_cronts[0][1]
            if now_interval != interval:
                jobs_list.append(
                    {'task': RepeatAlert, 'interval': now_interval})
                interval = now_interval
            if jobs_list:
                task.modify(jobs_list)
                logs.info('update task success')


if __name__ == '__main__':
    a = TaskDaemon()
    a.run()
