#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_charset.py
@Author  :   Billy Zhou
@Time    :   2021/03/12
@Version :   1.2.0
@Desc    :   None
'''


import sys
import logging
import chardet
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqldb.func_basic import row_func  # noqa: E402


def row_cor_charset(
        row, charset_decode='GBK', charset_encode='latin1', auto_detect=False):
    logging.debug('row: %s', row)
    row_cor = row_func(
        row, charset_correct, charset_encode=charset_encode,
        charset_decode=charset_decode, auto_detect=auto_detect)

    logging.debug('row_cor: %s', row_cor)
    return row_cor


def charset_correct(
        data, datatype, num_now, length,
        charset_encode, charset_decode, auto_detect):
    logging.debug('data: %s', data)
    if isinstance(data[1], str):
        if auto_detect:
            logging.debug('value_detect: %s', chardet.detect(
                data[1].encode(charset_encode)))
            value_cor = data[1].encode(charset_encode).decode(
                chardet.detect(data.encode(charset_encode))['encoding'])
        else:
            value_cor = data[1].encode(charset_encode).decode(charset_decode)
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
                # sql = '''SELECT [测试字段1] = '中文', [测试字段2] = 111 '''
                sql = 'SELECT TOP 10 * FROM cizu;'
                cursor.execute(sql)
                row = cursor.fetchone()
                # row = cursor.fetchall()
                row_cor = row_cor_charset(
                    row, charset_decode='GBK', charset_encode='utf-8',
                    auto_detect=True)
    except Exception as e:
        logging.debug("An error occurred. {}".format(e.args[-1]))
        if 'conn' in dir():
            conn.close()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
