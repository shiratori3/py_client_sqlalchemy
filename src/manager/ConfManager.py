#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ConfManager.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.Logger import logger  # noqa: E402
log = logger.get_logger(__name__)

from src.manager.BaseFileManager import BaseFileManager  # noqa: E402
from src.basic.input_check import input_default  # noqa: E402
from src.basic.input_check import input_checking_YN  # noqa: E402


class ConfManager(BaseFileManager):
    # manage the configuration file
    def __init__(self, conf_path=''):
        super().__init__(conf_path=conf_path)

        # Add cwd to conf_dict
        self.conf_dict['path']['cwd'] = self._cwd

        log.debug('ConfManager inited')

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
            print('The value of {0}[{1}] already existed. '.format(session, option))
            print('Existed value: {0}'.format(self.conf_dict[session][option]))
            print('Inputed value: {0}'.format(value))
            YN = input_checking_YN('Updated existed value with inputed value?')
            if YN == 'Y':
                print('Updated.')
                self.conf_dict[session][option] = value
            else:
                print('Canceled.')
        else:
            self.conf_dict[session][option] = value

        self._write_conf()

        # Add cwd to conf_dict
        self.conf_dict['path']['cwd'] = self._cwd


if __name__ == '__main__':
    conf = ConfManager()
    log.info('cwdPath: %s', conf.conf_dict['path']['cwd'])

    log.info(conf.read_conf())
    log.info(conf.conf_dict)
    conf.add_value('test', 'name', 'amy')
    log.info(conf.read_conf())
    log.info(conf.conf_dict)
