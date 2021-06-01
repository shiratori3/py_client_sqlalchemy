#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_basic.py
@Author  :   Billy Zhou
@Time    :   2021/03/12
@Version :   1.2.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


def sql_read(script_file, encoding='utf8'):
    try:
        sql = ''
        with open(str(script_file), encoding=encoding) as f:
            for line in f.readlines():
                sql = sql + line
        logging.info('plaintext: %s', sql)
        return sql
    except Exception as e:
        print('Got error {!r}, Errno is {}'.format(e, e.args))


def row_func(row, func, *args, **kwargs):
    logging.debug('row: %s', row)
    if row:
        # cursor.fetchall() return all rows as a list
        if isinstance(row, list):
            row_cor = row_fecthall(row, func, *args, **kwargs)
        # cursor.fetchone() return one row
        # cursor() return row as tuple
        elif isinstance(row, tuple):
            row_cor = row_tuple_func(row, func, *args, **kwargs)
        # cursor.fetchone() return one row
        # cursor(as_dict=True) return row as dict
        elif isinstance(row, dict):
            row_cor = row_dict_func(row, func, *args, **kwargs)
        else:
            print('Error. Unexpected row type.')
    else:
        print('Error. Blank row.')

    logging.debug('row_cor: %s', row_cor)
    return row_cor


def row_fecthall(row, func, *args, **kwargs):
    row_cor = []
    # cursor() return row as tuple
    if isinstance(row[0], tuple):
        for row_tuple in row:
            row_cor.append(row_tuple_func(
                row_tuple, func, *args, **kwargs))
    # cursor(as_dict=True) return row as dict
    elif isinstance(row[0], dict):
        for row_dict in row:
            row_cor.append(row_dict_func(
                row_dict, func, *args, **kwargs))
    else:
        print('Error. The first elements is not dict.')
    return row_cor


def row_tuple_func(row_tuple, func, *args, **kwargs):
    row_tuple_cor = ()
    logging.info('row_tuple: %s', row_tuple)
    length = len(row_tuple)
    logging.debug('length: %s', length)
    for i, j in enumerate(row_tuple):
        logging.debug('num: %s', i)
        logging.debug('value: %s', j)
        num_cor, value_cor = func(
            (None, j), datatype='tuple', num_now=i + 1, length=length,
            *args, **kwargs)
        logging.debug('value_cor: %s', value_cor)
        row_tuple_cor += (value_cor, )
    return row_tuple_cor


def row_dict_func(row_dict, func, *args, **kwargs):
    row_dict_cor = {}
    logging.debug('row_dict: %s', row_dict)
    length = len(row_dict)
    logging.debug('length: %s', length)
    for num, (i, j) in enumerate(row_dict.items()):
        logging.debug('num: %s', num)
        logging.debug('key: %s', i)
        logging.debug('value: %s', j)
        key_cor, value_cor = func(
            (i, j), datatype='dict', num_now=num + 1, length=length,
            *args, **kwargs)
        logging.debug('key_cor: %s', key_cor)
        logging.debug('value_cor: %s', value_cor)
        row_dict_cor[key_cor] = value_cor
    return row_dict_cor


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    row_fecthall_dict = [
        {'test1': 'sdsaewe', 'test2': 14575},
        {'test1': 1122, 'test2': 'awewe'}]
    row_fecthall_tuple = [('sdsaewe', 14575), (1122, 'awewe')]
    row_dict = {'test1': 'sdsaewe', 'test2': 14575}
    row_tuple = ('sdsaewe', 14575)

    def row_func_test(basic_data, datatype, num_now, length):
        logging.info('basic_data: %s', basic_data)
        logging.info('basic_data_type: %s', type(basic_data))
        logging.info('num_now: %s', num_now)
        logging.info('length: %s', length)
        if isinstance(basic_data[1], int):
            print(basic_data[1])
        else:
            print(len(basic_data[1]))
        return basic_data

    row_func(row_fecthall_tuple, row_func_test)

    # testing sql_read()
    from conf_manage import readConf  # noqa: E402
    cwdPath = Path(readConf()["path"]['cwd'])
    with open(cwdPath.joinpath('sqlscript\\sql_test.txt'),
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
