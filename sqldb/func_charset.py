#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_charset.py
@Author  :   Billy Zhou
@Time    :   2021/03/01
@Version :   1.1.0
@Desc    :   None
'''


import sys
import logging
import chardet
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqldb.func_basic import row_func  # noqa: E402


def row_cor_charset(row, charset_decode='GBK', auto_detect=False):
    logging.info('row: %s', row)
    row_cor = row_func(
        row, charset_correct,
        charset_decode=charset_decode, auto_detect=auto_detect)

    logging.info('row_cor: %s', row_cor)
    return row_cor


def charset_correct(
        data, datatype, num_now, length, charset_decode, auto_detect):
    logging.debug('data: %s', data)
    if isinstance(data[1], str):
        if auto_detect:
            logging.debug('value_detect: %s', chardet.detect(
                data[1].encode('latin1')))
            value_cor = data[1].encode('latin1').decode(
                chardet.detect(data.encode('latin1'))['encoding'])
        else:
            value_cor = data[1].encode('latin1').decode(charset_decode)
    else:
        value_cor = data[1]
    return (data[0], value_cor)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    from init_db import Sqldb  # noqa
    try:
        with Sqldb('localhost').create_conn(
                conn_db='test', conn_charset='utf8') as conn:
            # with conn.cursor(as_dict=True) as cursor:
            with conn.cursor() as cursor:
                sql = '''SELECT [测试字段1] = '中文', [测试字段2] = 111 '''
                cursor.execute(sql)
                col = cursor.description
                logging.info('Columns: %s', col)
                row = cursor.fetchone()
                # row = cursor.fetchall()
                row_cor = row_cor_charset(row)
    except Exception as e:
        print('Got error {!r}, Errno is {}'.format(e, e.args))
        conn.close()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
