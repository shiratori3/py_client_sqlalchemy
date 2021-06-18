#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_query.py
@Author  :   Billy Zhou
@Time    :   2021/03/12
@Version :   1.0.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqldb.func_basic import sql_read  # noqa: E402
from sqldb.func_charset import row_cor_charset  # noqa: E402
from sqldb.func_todf import row_to_df  # noqa: E402


def sql_query(
        conn, sql, to_file='', num_to_str=True,
        as_dict=True, fetchall=True,
        charset_cor_de='GBK', charset_cor_en='latin1', charset_detect=False):
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(sql)
        row = cursor.fetchall() if fetchall else cursor.fetchone()
        row = row_cor_charset(
            row,
            charset_encode=charset_cor_en, charset_decode=charset_cor_de,
            auto_detect=charset_detect
        ) if charset_cor_de else row
        df = row_to_df(
            row, cursor.description,
            num_to_str=num_to_str, to_file=to_file)
        return df


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    from sqldb.init_db import Sqldb
    from conf_manage import readConf  # noqa: E402
    cwdPath = Path(readConf()["path"]['cwd'])
    try:
        with Sqldb('164').create_conn(
                conn_db='JYFIN', conn_charset='utf8') as conn:
            sql = sql_read(cwdPath.joinpath(
                'gitignore\\sqlscript\\数值异常：首列均为年份数开头.txt'))
            outfile = 'D:\\test.xlsx'
            result = sql_query(
                conn, sql, to_file=outfile, num_to_str=True,
                as_dict=True, fetchall=True,
                charset_cor_de='GBK', charset_cor_en='latin1',
                charset_detect=False)
    except Exception as e:
        logging.debug("An error occurred. {}".format(e.args[-1]))
        if 'conn' in dir():
            conn.close()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
