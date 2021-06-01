#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   conf_manage.py
@Author  :   Billy Zhou
@Time    :   2021/03/26
@Version :   1.1.0
@Desc    :   None
'''


import os
import logging
import configparser
from settings import basic_path
from settings import conf_filename
from settings import conf_dict_init


def readConf(
        conf_path=basic_path, conf_fname=conf_filename,
        check_dict='', CaseSens=True):
    """
    读取conf_path下的conf_fname配置文件
    可与check_dict进行比对并合并
    """
    conf = configparser.ConfigParser()
    if CaseSens:
        # options for case sensitive
        conf.optionxform = str
    conf_filepath = str(conf_path.joinpath(conf_fname))

    if not check_dict:
        """
        非比对模式：
        存在conf_path下的conf_fname文件则读取，否则写入settings中的conf_dict_init
        """
        if os.path.exists(conf_filepath):
            conf.read(conf_filepath)
        else:
            writeConf(conf_path, conf_dict_init, conf_fname, CaseSens)
            conf.read(conf_filepath)
        return conf2dict(conf)
    else:
        """
        比对模式：
        存在conf_path下的conf_fname文件至conf_read则读取，否则conf_read留空。
        将check_dict与conf_read进行比对并合并，最终更新至conf_path下的conf_fname
        """
        conf_read = {}
        if os.path.exists(conf_filepath):
            conf.read(conf_filepath)
            conf_read = conf2dict(conf)
        conf_dict_checked = conf_dict_check(conf_read, check_dict)
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


def conf_dict_check(dict_uncheck, check_dict):
    """
    比较dict_uncheck与check_dict并把缺失项合并至dict_uncheck
    """
    dict_checked = dict_uncheck
    dict_compare = check_dict
    if not dict_uncheck:
        # if {} then merge all
        dict_checked = check_dict
    else:
        # merge missing
        for session, options_dict in check_dict.items():
            if session != 'compare_lvl':
                dict_check(
                    dict_uncheck, dict_compare, dict_checked,
                    session, options_dict, check_dict['compare_lvl'])
    return dict_checked


def dict_check(
        dict_uncheck, dict_compare, dict_checked, session, options_dict, compare_lvl_dict):
    if not dict_uncheck.get(session):
        dict_checked = dict(dict_uncheck, **dict_compare)
    else:
        for option, compare_lvl in options_dict.items():
            compare_path = session + '_' + option
            if not dict_uncheck[session].get(option):
                # merge the missing part to dict_uncheck
                dict_checked[session] = dict(
                    dict_uncheck[session], **dict_compare[session])
            else:
                # replace value or only check path exists or not
                if compare_lvl_dict.get(compare_path):
                    if compare_lvl_dict[compare_path] == 'equal':
                        if dict_uncheck[session][option] != str(dict_compare[session][option]):
                            dict_checked[session][option] = str(dict_compare[session][option])
                    elif compare_lvl_dict[compare_path] == 'exist':
                        if not os.path.exists(dict_uncheck[session][option]):
                            dict_checked[session][option] = str(dict_compare[session][option])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    conf_dict = readConf()
    logging.info('config: %s', conf_dict)
    logging.info('config["path"]: %s', conf_dict["path"])

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
