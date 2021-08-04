#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_basic.py
@Author  :   Billy Zhou
@Time    :   2021/08/04
@Version :   1.4.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]))


def sql_read(script_file, encoding='utf8'):
    try:
        sql = ''
        with open(str(script_file), encoding=encoding) as f:
            for line in f.readlines():
                sql = sql + line
        logging.debug('plaintext: %s', sql)
        return sql
    except Exception as e:
        logging.debug("An error occurred. {}".format(e.args[-1]))


def row_func(row, func, *args, **kwargs):
    logging.debug('row: %s', row)
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
            logging.error('Error. Unexpected row type.')
    else:
        logging.info('Blank row.')

    logging.debug('row_cor: %s', row_cor)
    return row_cor


def row_fecthall(row, func, *args, **kwargs):
    row_cor = []
    # cursor() return row as tuple
    if isinstance(row[0], tuple):
        for row_tuple in row:
            row_cor.append(row_tuple_func(
                row_tuple, func, *args, **kwargs))
    else:
        logging.error('Error. Unexpected row[0] type.')
    return row_cor


def row_tuple_func(row_tuple, func, *args, **kwargs):
    row_tuple_cor = ()
    logging.debug('row_tuple: %s', row_tuple)
    length = len(row_tuple)
    logging.debug('length: %s', length)
    for i, j in enumerate(row_tuple):
        num_cor, value_cor = func(
            (None, j), num_now=i + 1, length=length,
            *args, **kwargs)
        logging.debug('num: %s', i)
        logging.debug('value: %s', j)
        logging.debug('value_cor: %s', value_cor)
        row_tuple_cor += (value_cor, )
    return row_tuple_cor


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    row_fecthall_tuple = [('sdsaewe', 14575), (1122, 'awewe')]
    row_tuple = ('sdsaewe', 14575)

    def row_func_test(basic_data, num_now, length):
        logging.info('basic_data: %s', basic_data)
        logging.info('num_now: %s', num_now)
        logging.info('length: %s', length)
        if isinstance(basic_data[1], int):
            print(basic_data[1])
        else:
            print(len(basic_data[1]))
        return basic_data

    row_func(row_fecthall_tuple, row_func_test)

    # testing sql_read()
    from ConfManager import cwdPath  # noqa: E402
    with open(cwdPath.joinpath('gitignore\\sqlscript\\sql_test.txt'),
              'a+') as test_file:
        test_file.seek(0, 0)  # back to the start
        f = test_file.read()
        logging.debug(f)
        if f == '':
            logging.info('测试文件为空')
            test_file.write('SELECT 1')

    sql_read(cwdPath.joinpath('sqlscript\\sql_test.txt'))

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
