# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler


# 100M 日志切割一次，保留10份
def log_init(logger, path):
    log = RotatingFileHandler(path, maxBytes=100 * 1024 * 1024, backupCount=10)
    formats = logging.Formatter(
        '[ %(asctime)s ] [ %(levelname)s ] [ %(threadName)s ] '
        '[ %(funcName)s ] %(message)s')
    log.setFormatter(formats)
    logger.addHandler(log)
    logger.setLevel(logging.INFO)


logs = logging.getLogger()

if __name__ == '__main__':
    log_init(logs, '/tmp/test.log')
    logs.info('这是测试')
    logs.info('testfffffffxx sdfsd')
    logs.error('Errors now')
