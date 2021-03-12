#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func.py
@Author  :   Billy Zhou
@Time    :   2021/03/01
@Version :   1.0.0
@Desc    :   None
'''


import logging
import pyexcel as pe
from pathlib import Path


def excel_save(org_file, dest_file, encoding='GBK'):
    try:
        pe.save_as(
            file_name=org_file,
            dest_file_name=dest_file,
            encoding=encoding)
        print("Convert the file: " + org_file)
        print("            into: " + dest_file)
    except Exception as e:
        print('Got error {!r}, Errno is {}'.format(e, e.args))
        logging.info("exists: %s", Path(org_file).exists())
        logging.info("is_file: %s", Path(org_file).is_file())


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


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    # excel_save(
    #     'D:\\zhouzp\\__working__\\_每日跟踪\\_SVN规则更新进度.csv',
    #     'D:\\1.xlsx')

    # testing sql_read()
    with open(Path.cwd().joinpath('sqlscript\\sql_test.txt'),
              'a+') as test_file:
        test_file.seek(0, 0)  # back to the start
        f = test_file.read()
        logging.debug(f)
        if f == '':
            logging.info('测试文件为空')
            test_file.write('SELECT 1')
    sql_read(Path.cwd().joinpath('sqlscript\\sql_test.txt'))

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
