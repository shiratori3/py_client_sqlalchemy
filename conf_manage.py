#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   conf_manage.py
@Author  :   Billy Zhou
@Time    :   2021/06/14
@Version :   1.3.0
@Desc    :   None
'''


import os
import logging
import configparser
from pathlib import Path
from basic.input_check import input_checking_YN


def confInit():
    basic_path = Path(os.path.abspath(os.path.dirname(__file__)))
    basic_dict = {
        'path': {
            'cwd': basic_path,
            'conffile': Path(basic_path).joinpath('settings.conf'),
        },
    }
    if not os.path.exists(str(basic_dict['path']['conffile'])):
        writeConf(str(basic_path), basic_dict, 'settings.conf', True)
    return basic_dict


def readConf(
        conf_path=confInit()['path']['cwd'],
        conf_fname=confInit()['path']['conffile'].parts[-1],
        dict_for_checking='', CaseSens=True):
    """
    读取conf_path下的conf_fname配置文件
    可与dict_for_checking进行比对并合并
    """
    conf = configparser.ConfigParser()
    if CaseSens:
        # options for case sensitive
        conf.optionxform = str
    conf_filepath = str(conf_path.joinpath(conf_fname))

    if not dict_for_checking:
        """
        非比对模式：
        存在conf_path下的conf_fname文件则读取，否则返回False
        """
        if os.path.exists(conf_filepath):
            conf.read(conf_filepath)
            return conf2dict(conf)
        else:
            return False
    else:
        """
        比对模式：
        存在conf_path下的conf_fname文件至conf_dict_readed则读取，否则conf_dict_readed留空。
        将dict_for_checking与conf_dict_readed进行比对并合并，最终更新至conf_path下的conf_fname
        """
        conf_dict_readed = {}
        if os.path.exists(conf_filepath):
            conf.read(conf_filepath)
            conf_dict_readed = conf2dict(conf)
        conf_dict_checked = dict_compare(conf_dict_readed, dict_for_checking)
        writeConf(conf_path, conf_dict_checked, conf_fname, CaseSens)
    return conf_dict_checked


def writeConf(conf_path, conf_dict, conf_fname, CaseSens):
    """
    将conf_dict内容写入至conf_path下的conf_fname
    """
    conf = configparser.ConfigParser()
    if CaseSens:
        # options for case sensitive
        conf.optionxform = str
    for key, value in conf_dict.items():
        conf[key] = value

    with open(str(conf_path.joinpath(conf_fname)), 'w') as configfile:
        conf.write(configfile)


def conf2dict(config):
    """
    将configparser.ConfigParser().read()后的读取结果转成dict：

    conf = configparser.ConfigParser()
    conf.read()
    conf_dict = conf2dict(conf)
    """
    dictionary = {}
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            dictionary[section][option] = config.get(section, option)
    return dictionary


def dict_compare(dict_uncheck, dict_for_checking, diff_autoadd=True):
    """
    比较dict_uncheck与dict_for_checking并把缺失项合并至dict_uncheck
    """
    dict_checked = dict_uncheck
    if not dict_uncheck:
        if diff_autoadd:
            # missing all
            dict_checked = dict_for_checking
        else:
            selection = input_checking_YN('dict_uncheck is blank. Replace it with dict_for_checking?')
            if selection == 'Y':
                dict_checked = dict_for_checking
            else:
                logging.info('Canceled.')
    else:
        # check sessions
        for session, options_dict in dict_for_checking.items():
            dict_session_compare(
                dict_uncheck, dict_for_checking, dict_checked,
                session, diff_autoadd)
    return dict_checked


def dict_session_compare(
        dict_uncheck, dict_for_checking, dict_checked, session, diff_autoadd):
    if not dict_uncheck.get(session):
        # missing session
        if diff_autoadd:
            dict_checked[session] = dict_for_checking[session]
        else:
            tip_words = 'dict_uncheck[{0}] is missing. Add it with dict_for_checking[{0}]?'.format(session)
            selection = input_checking_YN(tip_words)
            if selection == 'Y':
                dict_checked[session] = dict_for_checking[session]
            else:
                logging.info('Canceled.')
    else:
        if type(dict_uncheck[session]) == dict:
            # option_dict exist
            for option, value in dict_uncheck[session].items():
                dict_option_compare(
                    dict_uncheck, dict_for_checking, dict_checked,
                    session, option, diff_autoadd)
        else:
            # option_dict not exist, compare value
            if dict_uncheck[session] != str(dict_for_checking[session]):
                print('Values diff between dict_uncheck[{0}] and dict_for_checking[{0}].'.format(session))
                print('Value of dict_uncheck[{0}]: {1}'.format(session, dict_uncheck[session]))
                print('Value of dict_for_checking[{0}]: {1}'.format(session, dict_for_checking[session]))
                tip_words = 'Replace the value of dict_uncheck[{0}] with dict_for_checking[{0}]?'.format(session)
                selection = input_checking_YN(tip_words)
                if selection == 'Y':
                    dict_checked[session] = str(dict_for_checking[session])
                else:
                    logging.info('Canceled.')


def dict_option_compare(
        dict_uncheck, dict_for_checking, dict_checked, session, option, diff_autoadd):
    if not dict_uncheck[session].get(option):
        # missing option
        if diff_autoadd:
            dict_checked[session][option] = dict_for_checking[session][option]
        else:
            tip_words = 'dict_uncheck[{0}][{1}] is missing. Add it with dict_for_checking[{0}][{1}]?'.format(
                session, option)
            selection = input_checking_YN(tip_words)
            if selection == 'Y':
                dict_checked[session][option] = dict_for_checking[session][option]
            else:
                logging.info('Canceled.')
    else:
        # compare value
        if dict_uncheck[session][option] != str(dict_for_checking[session][option]):
            print('Values diff between dict_uncheck[{0}][{1}] and dict_for_checking[{0}][{1}].'.format(session, option))
            print('Value of dict_uncheck[{0}][{1}]: {2}'.format(session, option, dict_uncheck[session][option]))
            print('Value of dict_for_checking[{0}][{1}]: {2}'.format(session, option, dict_for_checking[session][option]))
            tip_words = 'Replace the value of dict_uncheck[{0}][{1}] with dict_for_checking[{0}][{1}]?'.format(session, option)
            selection = input_checking_YN(tip_words)
            if selection == 'Y':
                dict_checked[session][option] = str(dict_for_checking[session][option])
            else:
                logging.info('Canceled.')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    conf_dict = readConf()
    logging.info('config: %s', conf_dict)
    logging.info('config["path"]["cwd"]: %s', conf_dict['path']['cwd'])
    logging.info('config["path"]["conffile"]: %s', conf_dict['path']['conffile'])

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
