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

from src.manager.LogManager import logmgr
log = logmgr.get_logger(__name__)

import copy
from collections.abc import Mapping
from src.basic.input_check import input_checking_YN, input_checking_list


def dict_compare(
        dict1_uncheck: dict, dict2_uncheck: dict,
        miss_checkmode: str = 'ADD', diff_checkmode: str = 'CONFIRM',
        dict1_checked: dict = {}, dict2_checked: dict = {},
        suffix: str = '[]', lv: int = 0) -> dict:
    """Compare two dict and merge the missing part base on dict2_uncheck"""
    if not dict1_checked and not dict2_checked:
        # init
        if miss_checkmode.upper() not in ('ADD', 'IGNORE', 'CONFIRM'):
            raise KeyError(f'Unvaild miss_checkmode[{miss_checkmode}]')
        else:
            miss_checkmode = miss_checkmode.upper()
        if diff_checkmode.upper() not in ('IGNORE', 'CONFIRM'):
            raise KeyError(f'Unvaild diff_checkmode[{diff_checkmode}]')
        else:
            diff_checkmode = diff_checkmode.upper()
        dict1_checked = copy.deepcopy(dict1_uncheck)
        dict2_checked = copy.deepcopy(dict2_uncheck)
    sub_lv = lv + 1
    suffix = '[]' if lv == 0 else suffix
    if set(dict1_uncheck.keys()) | set(dict2_uncheck.keys()):
        if not dict1_uncheck or not dict2_uncheck:
            log.info(f'dict1_uncheck: {dict1_uncheck}')
            log.info(f'dict2_uncheck: {dict2_uncheck}')
            # missing part
            if not miss_checkmode == 'IGNORE':
                miss_add = False
                if not miss_checkmode == 'ADD':
                    miss_dict_name = 'dict1_checked' if not dict1_checked else 'dict2_checked'
                    if input_checking_YN(f'{miss_dict_name}{suffix} is blank. Fill it?') == 'Y':
                        print('Filled.')
                        miss_add = True
                    else:
                        print('Canceled.')
                if miss_checkmode == 'ADD' or miss_add:
                    if not dict1_checked:
                        dict1_checked = dict2_checked
                    else:
                        dict2_checked = dict1_checked
        else:
            log.debug(f'dict1_checked: {dict1_checked}')
            log.debug(f'dict2_checked: {dict2_checked}')
            # diff between dict1_uncheck and dict2_uncheck base on the union set of their keys
            for key in set(dict1_uncheck.keys()) | set(dict2_uncheck.keys()):
                log.debug(f"sub_lv: {sub_lv}")
                log.debug(f"suffix: {suffix}")
                sub_suffix = suffix + "[" + str(key) + "]" if suffix != '[]' else "[" + str(key) + "]"
                log.debug(f"sub_suffix: {sub_suffix}")
                if dict1_uncheck.get(key, None) is None or dict1_uncheck.get(key, None) is None:
                    # dict_uncheck missing part in another dict_uncheck
                    if not miss_checkmode == 'IGNORE':
                        miss_add = False
                        if not miss_checkmode == 'ADD':
                            miss_dict_name = 'dict1_checked' if dict1_uncheck.get(
                                key, None) is None else 'dict2_checked'
                            tip_words = f'{miss_dict_name}{sub_suffix} is missing. Add it?'
                            if input_checking_YN(tip_words) == 'Y':
                                print(f'{miss_dict_name}{sub_suffix} Added.')
                                miss_add = True
                            else:
                                print('Canceled.')
                        if miss_checkmode == 'ADD' or miss_add:
                            if dict1_uncheck.get(key, None) is None:
                                dict1_checked[key] = dict2_uncheck[key]
                            else:
                                dict2_checked[key] = dict1_uncheck[key]
                else:
                    log.debug(f"dict1_uncheck{sub_suffix}: {dict1_uncheck.get(key, None)}")
                    log.debug(f"dict2_uncheck{sub_suffix}: {dict2_uncheck.get(key, None)}")
                    if isinstance(dict1_uncheck.get(key, None), Mapping) and isinstance(
                            dict2_uncheck.get(key, None), Mapping):
                        # if both value of dict_uncheck is a mapping type, check deeper
                        dict_compare(
                            dict1_uncheck[key], dict2_uncheck[key],
                            miss_checkmode, diff_checkmode,
                            dict1_checked[key], dict2_checked[key], sub_suffix, sub_lv)
                    else:
                        # check diff part of values between dict1_uncheck and dict2_uncheck
                        if str(dict1_uncheck.get(key, None)) != str(dict2_uncheck.get(key, None)):
                            if not diff_checkmode == 'IGNORE':
                                print('Values diff between dict1_uncheck{0} and dict2_uncheck{0}.'.format(sub_suffix))
                                print('Value of dict1_uncheck{0}: {1}'.format(sub_suffix, dict1_uncheck.get(key, None)))
                                print('Value of dict2_uncheck{0}: {1}'.format(sub_suffix, dict2_uncheck.get(key, None)))
                                tip_words = 'Keep the diff between dict1_uncheck{0} and dict2_uncheck{0}?'.format(sub_suffix)
                                if input_checking_YN(tip_words, default_Y=False) == 'N':
                                    tip_words = 'Keep which one? Input 3 to cancel, 1 for dict1_uncheck{0}, 2 for dict2_uncheck{0}.'.format(sub_suffix)
                                    inputed = input_checking_list(['1', '2', '3'], tip_words)
                                    if inputed == '1':
                                        if dict1_uncheck.get(key, None) is not None:
                                            dict2_checked[key] = dict1_uncheck[key]
                                        else:
                                            print('Since dict1_uncheck{0} is None, drop dict2_uncheck{0}'.format(sub_suffix))
                                            dict2_checked.pop(key)
                                        print('Replace dict2_uncheck{0} with dict1_uncheck{0}'.format(sub_suffix))
                                    elif inputed == '2':
                                        if dict2_uncheck.get(key, None) is not None:
                                            dict1_checked[key] = dict2_uncheck[key]
                                        else:
                                            print('Since dict2_uncheck{0} is None, drop dict1_uncheck{0}'.format(sub_suffix))
                                            dict1_checked.pop(key)
                                        print('Replace dict1_uncheck{0} with dict2_uncheck{0}'.format(sub_suffix))
                                    else:
                                        print('Canceled.')
                                else:
                                    print('Canceled.')
    return dict1_checked, dict2_checked


if __name__ == '__main__':
    d1 = {
        1: {
            2: {
                7: [9],  # miss
                8: [10],  # diff
            },
            6: [7, 8]  # miss
        },
        4: [7, 8],  # diff
        5: [5, 6],  # miss
    }
    d2 = {
        1: {
            2: {
                8: [7],  # diff
                9: [10]  # miss
            },
            3: [7, 8]  # miss
        },
        2: {
            1: {},
        },  # missing
        3: [7, 8],  # miss
        4: [5, 6],  # diff
    }

    print("d1: {0}".format(d1))
    print("d2: {0}".format(d2))
    if False:
        d1, d2 = dict_compare(d1, d2, miss_checkmode='add', diff_checkmode='confirm')
    elif True:
        d1, d2 = dict_compare(d1, d2, miss_checkmode='confirm', diff_checkmode='ignore')
    elif True:
        d1, d2 = dict_compare(d1, d2, miss_checkmode='ignore', diff_checkmode='ignore')
    print("d1: {0}".format(d1))
    print("d2: {0}".format(d2))
