#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test.py
@Author  :   Billy Zhou
@Time    :   2021/03/01
@Version :   1.0.0
@Desc    :   None
'''


import logging

from pathlib import Path
from sqldb.init_db import Sqldb
from sqldb.func_charset import row_cor_charset
from sqldb.func_todf import row_to_df
from basic.func import sql_read


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    try:
        with Sqldb('164').create_conn(
                conn_db='JYFIN', conn_charset='utf8') as conn:
            # with conn.cursor() as cursor:
            with conn.cursor(as_dict=True) as cursor:
                sql = sql_read(Path.cwd().joinpath(
                    'gitignore\\sqlscript\\数值异常：首列均为年份数开头.txt'))
                cursor.execute(sql)
                # row = cursor.fetchone()
                row = cursor.fetchall()
                row_cor = row_cor_charset(row, 'GBK')
                df = row_to_df(
                    row_cor, cursor.description,
                    num_to_str=True, to_file='D:\\test.xlsx')
    except Exception as e:
        print('Got error {!r}, Errno is {}'.format(e, e.args))
        conn.close()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
