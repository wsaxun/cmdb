# -*- coding: utf-8 -*-
import os
import codecs
import ConfigParser

__all__ = ['config']


class Config(object):
    def __init__(self, cfgpath):
        self.cfg = {}
        self.config_parser(cfgpath)

    def config_parser(self, cfg_path):
        conf = ConfigParser.ConfigParser()
        fb = codecs.open(cfg_path, 'r', 'utf-8-sig')
        conf.readfp(fb)
        for i in conf.sections():
            for n in conf.options(i):
                key = i + '_' + n
                self.cfg[key] = conf.get(i, n)

    @property
    def config(self):
        return self.cfg

    @config.setter
    def config(self, configs):
        if isinstance(configs, dict):
            if configs:
                self.cfg = configs
            else:
                raise Exception('dict is None')
        else:
            raise ValueError('Please give a dict')


config = Config(os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, '../config/collect.conf')))
