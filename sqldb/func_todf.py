#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_todf.py
@Author  :   Billy Zhou
@Time    :   2021/03/01
@Version :   1.1.0
@Desc    :   None
'''


import os
import sys
import logging
import pandas as pd
import pyexcel as pe
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqldb.func_basic import row_func  # noqa: E402
from basic.to_excel import df_to_excel  # noqa: E402


def row_to_df(row, col, num_to_str=False, to_file=''):
    '''turn row to dataframe.

    Args:
        row (list): cursor.fetchall(). a list of row values
        col (tuple): cursor.description
        to_file (str): path of the file to save. Support .csv,
            .xls, and .xlsx

    Returns:
        BufferedFileStorage: A buffered writable file descriptor
    '''
    # col = cursor.description
    logging.debug('Columns: %s', col)
    logging.debug('row: %s', row)
    logging.debug('type(row): %s', type(row))
    col_list = []
    for i in range(len(col)):
        col_list.append(col[i][0])
    logging.debug('col: %s', col_list)
    df_list = []
    df_list.append(col_list)
    row_func(row, data_to_df, df_data=df_list, num_to_str=num_to_str)

    df = pd.DataFrame(df_list[1:], columns=df_list[0])
    logging.info('df_from_row: %s', df)

    if to_file:
        df_to_excel(df, to_file, num_to_str)
    return df


def data_to_df(data, df_data, num_to_str, datatype, num_now, length):
    logging.debug('data: %s', data)
    logging.debug('df_data: %s', df_data)
    logging.debug('num_now: %s', num_now)
    logging.debug('length: %s', length)
    logging.debug('len(df_data): %s', len(df_data))

    data_value = data[1]
    if num_to_str:
        if isinstance(data[1], (int, float)):
            data_value = str(data[1])
    logging.debug('data: %s', data_value)

    value_list = []
    if len(df_data) == 1 or len(df_data[-1]) == length:
        value_list.append(data_value)
        df_data.append(value_list)
    else:
        df_data[-1].append(data_value)
    return data


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    from sqldb.init_db import Sqldb
    try:
        with Sqldb('localhost').create_conn(
                conn_db='test', conn_charset='utf8') as conn:
            # with conn.cursor() as cursor:
            with conn.cursor(as_dict=True) as cursor:
                sql = 'SELECT TOP 10 * FROM cizu;'
                cursor.execute(sql)
                row = cursor.fetchall()
                # logging.info('row: %s', row)
                # logging.info('type(row): %s', type(row))
                df = row_to_df(
                    row, cursor.description,
                    num_to_str=True, to_file='D:\\test_todf.xlsx')
    except Exception as e:
        print('Got error {!r}, Errno is {}'.format(e, e.args))
        conn.close()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
