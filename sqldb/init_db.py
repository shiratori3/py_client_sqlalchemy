#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   init_db.py
@Author  :   Billy Zhou
@Time    :   2021/03/01
@Version :   1.0.0
@Desc    :   None
'''


import sys
import logging
import pymssql  # import _mssql
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from conn_info import check_conn_info  # noqa: E402
from settings import setting_basic  # noqa: E402


class Sqldb(object):
    def __init__(self, conn_name):
        self.name = conn_name

    def create_conn(self, conn_db='', conn_charset='utf8'):
        conn_info = check_conn_info(
            self.name, encrypt=True,
            pubkeyfile=setting_basic['pubkeyfile'],
            prikeyfile=setting_basic['prikeyfile']
        )
        if not conn_db:
            conn_db = conn_info['database']
        self.conn = pymssql.connect(
            host=conn_info['host'],
            database=conn_db,
            user=conn_info['user'],
            password=conn_info['pwd'],
            charset=conn_charset
        )
        return self.conn


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    from sqldb.func_todf import row_to_df
    try:
        with Sqldb('localhost').create_conn(
                conn_db='test', conn_charset='utf8') as conn:
            # with conn.cursor() as cursor:
            with conn.cursor(as_dict=True) as cursor:
                sql = 'SELECT TOP 500 * FROM cizu;'
                cursor.execute(sql)
                # row = cursor.fetchone()
                row = cursor.fetchall()
                df = row_to_df(
                    row, cursor.description,
                    num_to_str=True, to_file='D:\\test_500.xls')
    except Exception as e:
        print('Got error {!r}, Errno is {}'.format(e, e.args))
        conn.close()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
