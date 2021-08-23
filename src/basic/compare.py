#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   compare.py
@Author  :   Billy Zhou
@Time    :   2021/08/22
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.Logger import logger
log = logger.get_logger(__name__)

import copy
from collections.abc import Mapping
from src.basic.input_check import input_checking_YN


def dict_compare(
        dict_uncheck: dict, dict_refer: dict,
        dict_checked: dict = {}, suffix: str = '[]', lv: int = 0, diff_autoadd=True) -> dict:
    """Compare two dict and merge the missing part."""
    if not dict_checked:
        log.debug('dict_checked init')
        dict_checked = copy.deepcopy(dict_uncheck)
    sub_lv = lv + 1
    suffix = '[]' if lv == 0 else suffix
    if not dict_uncheck:
        # missing part
        if diff_autoadd:
            dict_checked = dict_refer
        else:
            selection = input_checking_YN('dict_uncheck is blank. Fill it with dict_refer?')
            if selection == 'Y':
                print('Filled.')
                dict_checked = dict_refer
            else:
                print('Canceled.')
    else:
        log.debug('dict_checked: {0}'.format(dict_checked))
        # diff with dict_refer base on dict_refer.items()
        for key, value_refer in dict_refer.items():
            suffix_ = "[" + str(key) + "]"
            log.debug("sub_lv: %s", sub_lv)
            log.debug("suffix: %s", suffix)
            log.debug("suffix_: %s", suffix_)
            if not dict_uncheck.get(key):
                # dict_uncheck missing part in dict_refer
                if diff_autoadd:
                    dict_checked[key] = dict_refer[key]
                else:
                    sub_suffix = suffix + suffix_ if suffix != '[]' else suffix_
                    tip_words = 'dict_uncheck{0} is missing. Add it with dict_refer{0}?'.format(sub_suffix)
                    selection = input_checking_YN(tip_words)
                    if selection == 'Y':
                        print('Added.')
                        dict_checked[key] = dict_refer[key]
                    else:
                        print('Canceled.')
            else:
                sub_suffix = suffix + suffix_ if suffix != '[]' else suffix_
                if isinstance(value_refer, Mapping):
                    # check deeper for dict type of value_refer
                    # value_refer equal to dict_refer[key]
                    log.debug("sub_suffix: %s", sub_suffix)
                    dict_compare(
                        dict_uncheck[key], value_refer, dict_checked[key],
                        sub_suffix, sub_lv, diff_autoadd)
                else:
                    # check diff part of values between dict_uncheck and dict_refer
                    if str(dict_uncheck[key]) != str(dict_refer[key]):
                        print('Values diff between dict_uncheck{0} and dict_refer{0}.'.format(sub_suffix))
                        print('Value of dict_uncheck{0}: {1}'.format(sub_suffix, dict_uncheck[key]))
                        print('Value of dict_refer{0}: {1}'.format(sub_suffix, value_refer))
                        tip_words = 'Replace the value of dict_uncheck{0} with dict_refer{0}?'.format(sub_suffix)
                        selection = input_checking_YN(tip_words)
                        if selection == 'Y':
                            print('Replaced.')
                            dict_checked[key] = dict_refer[key]
                        else:
                            print('Canceled.')
    return dict_checked


if __name__ == '__main__':
    d1 = {
        1: {
            2: {
                7: [9]
            },
            6: [7, 8]
        },
        4: [7, 8]
    }
    d2 = {
        1: {
            2: {
                9: [10]
            },
            3: [7, 8]
        },
        2: {
            1: {},
        },
        3: [7, 8],
        4: [5, 6],
    }

    print(dict_compare(d1, d2, diff_autoadd=False))
    print("d1: {0}".format(d1))
    print("d2: {0}".format(d2))
