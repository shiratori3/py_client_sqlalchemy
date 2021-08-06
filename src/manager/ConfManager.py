#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ConfManager.py
@Author  :   Billy Zhou
@Time    :   2021/08/06
@Version :   1.5.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2]))

from src.basic.input_check import input_default  # noqa: E402
from src.basic.input_check import input_checking_YN  # noqa: E402
from src.manager.BaseManager import BaseFileManager  # noqa: E402


class ConfManager(BaseFileManager):
    # manage the configuration file
    def __init__(self, conf_path=''):
        super().__init__(conf_path=conf_path)

        # Add cwd to conf_dict
        self.conf_dict['path']['cwd'] = self._cwd

    def add_value(self, session='', option='', value='') -> None:
        self.conf_dict = self.read_conf()
        if not (session and option and value):
            session = input_default(
                'session', 'Please input the session name to ADD.')
            option = input_default(
                'option', 'Please input the option of {0} to ADD.'.format(session))
            value = input_default(
                'value', 'Please input the value of {0}[{1}] to ADD.'.format(session, option))
        if not self.conf_dict.get(session):
            self.conf_dict[session] = {}
        if self.conf_dict[session].get(option):
            logging.info('The value of {0}[{1}] already existed. '.format(session, option))
            logging.info('Existed value: {0}'.format(self.conf_dict[session][option]))
            logging.info('Inputed value: {0}'.format(value))
            YN = input_checking_YN('Updated existed value with inputed value?')
            if YN == 'Y':
                logging.info('Updated.')
                self.conf_dict[session][option] = value
            else:
                logging.info('Canceled.')
        else:
            self.conf_dict[session][option] = value

        self._write_conf()

        # Add cwd to conf_dict
        self.conf_dict['path']['cwd'] = self._cwd


conf = ConfManager()
cwdPath = conf.conf_dict['path']['cwd']
logging.info('cwdPath: %s', cwdPath)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        # filename=os.path.basename(__file__) + '_' + time.strftime('%Y%m%d', time.localtime()) + '.log',
        # filemode='a',
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    # conf = ConfManager('d:\\')
    # cwdPath = conf.conf_dict
    # logging.info('cwdPath: %s', cwdPath)

    # print(conf.read_conf())
    # print(conf.conf_dict)
    # conf.add_value('test', 'name', 'amy')
    # print(conf.read_conf())
    # print(conf.conf_dict)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
