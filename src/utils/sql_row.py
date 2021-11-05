#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   row_func.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr
log = logmgr.get_logger(__name__)


def row_func(row, func, *args, **kwargs):
    log.debug('row: %s', row)
    row_cor = ()
    if row:
        # cursor.fetchall() return all rows as a list of tuples
        if isinstance(row, list):
            row_cor = row_fecthall(row, func, *args, **kwargs)
        # cursor.fetchone() return one row
        # cursor() return row as tuple
        elif isinstance(row, tuple):
            row_cor = row_tuple_func(row, func, *args, **kwargs)
        else:
            log.error('Error. Unexpected row type.')
    else:
        log.info('Blank row.')

    log.debug('row_cor: %s', row_cor)
    return row_cor


def row_fecthall(row, func, *args, **kwargs):
    row_cor = []
    # cursor() return row as tuple
    if isinstance(row[0], tuple):
        for row_tuple in row:
            row_cor.append(row_tuple_func(
                row_tuple, func, *args, **kwargs))
    else:
        log.error('Error. Unexpected row[0] type.')
    return row_cor


def row_tuple_func(row_tuple, func, *args, **kwargs):
    row_tuple_cor = ()
    log.debug('row_tuple: %s', row_tuple)
    length = len(row_tuple)
    log.debug('length: %s', length)
    for i, j in enumerate(row_tuple):
        num_cor, value_cor = func(
            (None, j), num_now=i + 1, length=length,
            *args, **kwargs)
        log.debug('num: %s', i)
        log.debug('value: %s', j)
        log.debug('value_cor: %s', value_cor)
        row_tuple_cor += (value_cor, )
    return row_tuple_cor


if __name__ == '__main__':
    row_fecthall_tuple = [('sdsaewe', 14575), (1122, 'awewe')]
    row_tuple = ('sdsaewe', 14575)

    def row_func_test(basic_data, num_now, length):
        log.info('basic_data: %s', basic_data)
        log.info('num_now: %s', num_now)
        log.info('length: %s', length)
        if isinstance(basic_data[1], int):
            print(basic_data[1])
        else:
            print(len(basic_data[1]))
        return basic_data

    row_func(row_fecthall_tuple, row_func_test)
