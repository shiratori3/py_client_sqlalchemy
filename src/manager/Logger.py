#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Logger.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

import yaml
import logging
import logging.config


class Logger:
    def __init__(self, conf: Path = cwdPath.joinpath('logging.yaml'), default_lv=logging.INFO) -> None:
        self.conf_file = conf
        if self.conf_file.exists():
            with open(self.conf_file, encoding='utf-8') as f:
                try:
                    self.config = yaml.safe_load(f.read())
                    for handler_name, dict_value in self.config['handlers'].items():
                        if dict_value.get('filename'):
                            filename = self.config['handlers'][handler_name]['filename']
                            logpath = Path(cwdPath.joinpath(filename)).parents[0]
                            if not logpath.exists():
                                logpath.mkdir(parents=True)
                            self.config['handlers'][handler_name]['filename'] = str(cwdPath.joinpath(filename))
                            # print(config['handlers'][handler_name]['filename'])
                    self.logger_list = list(self.config['loggers'].keys())
                    logging.config.dictConfig(self.config)
                    self.log = logging.getLogger(__name__)
                    self.log.info('The config of loggers is loaded')
                except Exception as e:
                    self.logger_list = []
                    logging.basicConfig(level=default_lv)
                    self.log = logging.getLogger(__name__)
                    self.log.error('Failed to load config in logging.yaml. Using the default configs.')
                    self.log.error("An error occurred. {}".format(e.args[-1]))
        else:
            self.logger_list = []
            logging.basicConfig(level=default_lv)
            self.log = logging.getLogger(__name__)
            self.log.error('logging.yaml not exists in [{}]. Using the default configs.'.format(conf))
        self.log.info('logger inited')

    def get_logger(self, name=''):
        if self.logger_list:
            if name in self.logger_list:
                return logging.getLogger(name)
            else:
                self.log.debug('get_logger name[{}] not in logger_list'.format(name))
                return logging.getLogger()
        else:
            self.log.debug('logger_list not exists'.format())
            return logging.getLogger()


logger = Logger()

if __name__ == '__main__':
    log = logger.get_logger(__name__)
    print(log)
