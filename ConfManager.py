#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ConfManager.py
@Author  :   Billy Zhou
@Time    :   2021/08/01
@Version :   1.0.0
@Desc    :   None
'''


import os
import logging
import configparser
from pathlib import Path
from basic.input_check import input_default
from basic.input_check import input_checking_YN


class ConfManager(object):
    def __init__(self, inputed_path: Path = '', CaseSens: bool = True):
        self._CaseSens = CaseSens
        self._cwd = Path(os.path.abspath(os.path.dirname(__file__)))
        self._conf_path = Path(inputed_path)
        self._conf_file = Path(inputed_path).joinpath('settings.conf')
        self._default_path = {
            'path': {
                'confpath': self._cwd,
            },
        }

        # check _conf_file
        if not self._conf_file.exists():
            # check inputed path and is_dir() and exists()
            logging.debug("conf_path before checked: %s", self._conf_path)
            if self._conf_path == Path('') or str(self._conf_path) == '.':
                self._conf_path = self._cwd
                logging.warning('Blank inputed path. Using the default path[{0}]'.format(self._cwd))
            if not Path(self._conf_path).is_dir():
                self._conf_path = self._cwd
                logging.warning('Unvaild inputed path. Using the default path[{0}]'.format(self._cwd))
            if not Path(self._conf_path).exists():
                Path(self._conf_path).mkdir(parents=True)
                logging.info("The path[{0}] not existed. Creating.".format(self._conf_path))
            logging.debug("conf_path after checked: %s", self._conf_path)
            self._conf_file = self._conf_path.joinpath('settings.conf')
            self.conf_dict = {
                'path': {
                    'confpath': self._conf_path,
                },
            }
        else:
            self.conf_dict = self.readConf()
            # check readed conf_dict
            for key, value in self._default_path['path'].items():
                if not self.conf_dict['path'].get(key):
                    self.conf_dict['path'][key] = value
                    logging.info('The configuration missing the part[{0}]'.format(key))
                    logging.info('Adding with the default value[{0}]'.format(value))
                else:
                    if key == 'confpath':
                        if Path(self.conf_dict['path']['confpath']) != Path(inputed_path):
                            self.conf_dict['path']['confpath'] = Path(inputed_path)

        # Update the conf file
        self.writeConf()

        # Add cwd to conf_dict
        self.conf_dict['path']['cwd'] = self._cwd

    def writeConf(self) -> None:
        conf = configparser.ConfigParser()
        if self._CaseSens:
            # options for case sensitive
            conf.optionxform = str
        for key, value in self.conf_dict.items():
            conf[key] = value

        with open(str(self._conf_file), 'w') as configfile:
            conf.write(configfile)

    def _conf2dict(self, config: configparser.ConfigParser) -> dict:
        # convert the ConfigParser to dict
        dictionary = {}
        for section in config.sections():
            dictionary[section] = {}
            for option in config.options(section):
                dictionary[section][option] = config.get(section, option)
        return dictionary

    def readConf(self) -> dict or False:
        conf = configparser.ConfigParser()
        if self._CaseSens:
            # options for case sensitive
            conf.optionxform = str

        if self._conf_file.exists():
            conf.read(self._conf_file)
            return self._conf2dict(conf)
        else:
            logging.error(
                'The configuration file not exists in path[{0}]'.format(
                    self._conf_file))
            return False

    def addConf(self, session='', option='', value='') -> None:
        self.conf_dict = self.readConf()
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
        self.writeConf()

        # Add cwd to conf_dict
        self.conf_dict['path']['cwd'] = self._cwd


conf = ConfManager()
cwdPath = conf.conf_dict
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

    conf_test = ConfManager('F:\\')
    print(conf_test.readConf())
    print(conf_test.conf_dict)
    conf_test.addConf('test', 'name', 'amy')
    print(conf_test.readConf())
    print(conf_test.conf_dict)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
