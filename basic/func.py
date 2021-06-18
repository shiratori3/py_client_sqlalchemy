#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func.py
@Author  :   Billy Zhou
@Time    :   2021/03/12
@Version :   1.2.0
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
        logging.info("Convert the file: " + org_file)
        logging.info("            into: " + dest_file)
    except Exception as e:
        logging.debug("An error occurred. {}".format(e.args[-1]))
        logging.info("exists: %s", Path(org_file).exists())
        logging.info("is_file: %s", Path(org_file).is_file())


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

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
