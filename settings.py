#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   setting.py
@Author  :   Billy Zhou
@Time    :   2021/03/01
@Version :   1.0.0
@Desc    :   None
'''


import logging

from pathlib import Path

setting_basic = {
    'pubkeyfile': Path.cwd().joinpath('gitignore\\rsa\\public.pem'),
    'prikeyfile': Path.cwd().joinpath('gitignore\\rsa\\private.pem'),
}


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    logging.info('setting_basic: %s', setting_basic)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
