#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   compare.py
@Author  :   Billy Zhou
@Time    :   2021/08/01
@Version :   0.1.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]))

from basic.input_check import input_checking_YN  # noqa: E402


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
        # filename=os.path.basename(__file__) + '_' + time.strftime('%Y%m%d', time.localtime()) + '.log',
        # filemode='a',
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
