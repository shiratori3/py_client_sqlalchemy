#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   init_db.py
@Author  :   Billy Zhou
@Time    :   2021/06/15
@Version :   1.2.0
@Desc    :   None
'''


import sys
import logging
import pymssql  # import _mssql
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from conn_manager import conn_manager  # noqa: E402
from conf_manage import readConf  # noqa: E402


class Sqldb(object):
    def __init__(self, conn_name):
        self.name = conn_name

    def create_conn(self, conn_db='', conn_charset='utf8'):
        conn_info = conn_manager(
            'READ', conn_name=self.name,
            conn_path=Path(readConf()["path"]['cwd']).joinpath('gitignore\\conn'),
            encrypt=True
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

    from sqldb.func_query import sql_query
    try:
        with Sqldb('localhost').create_conn(
                conn_db='test', conn_charset='utf8') as conn:
            sql = 'SELECT TOP 1 * FROM cizu;'
            result = sql_query(
                conn, sql, to_file='D:\\test.xlsx', num_to_str=True,
                as_dict=True, fetchall=True,
                charset_cor_de='UTF8', charset_cor_en='UTF8')
    except Exception as e:
        print('Got error {!r}, Errno is {}'.format(e, e.args))
        if conn:
            conn.close()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
