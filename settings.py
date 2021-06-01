#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   settings.py
@Author  :   Billy Zhou
@Time    :   2021/03/26
@Version :   1.3.0
@Desc    :   None
'''


import os
import logging
from pathlib import Path

basic_path = Path(os.path.abspath(os.path.dirname(__file__)))
# basic_path = Path('D:\\pycharm\\py_for_mssql')
conf_filename = 'py_for_mssql.conf'
conf_dict_init = {
    'path': {
        'cwd': basic_path,
    },
    'RsaKey': {
        'pubkeyfile': basic_path.joinpath('gitignore\\rsa\\public.pem'),
        'prikeyfile': basic_path.joinpath('gitignore\\rsa\\private.pem'),
    },
    'compare_lvl': {
        'path_cwd': 'equal',
        'RsaKey_pubkeyfile': 'exist',
        'RsaKey_prikeyfile': 'exist',
    },
}


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    logging.info('basic_path: %s', basic_path)
    logging.info('conf_filename: %s', conf_filename)
    logging.info('conf_dict_init: %s', conf_dict_init)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
