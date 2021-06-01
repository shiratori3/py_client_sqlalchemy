#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   input_check.py
@Author  :   Billy Zhou
@Time    :   2021/03/01
@Version :   1.2.0
@Desc    :   None
'''


import logging
import getpass


def input_default(input_data, default_word=''):
    if input_data.strip() == '':
        print('Blank input. Using the default value: {0}'.format(default_word))
        return default_word
    else:
        return input_data


def input_pwd(tip_words='Please input your password:'):
    return getpass.getpass(tip_words)


def input_checking_YN(tip_words='Please input words.'):
    input_value = input_default(input(tip_words + '[Y]/N: '), 'Y').upper()
    logging.debug(input_value)

    while not (set([input_value]) & set(['Y', 'N'])):
        print('Unexpect input! Please input Y or N.')
        input_value = input_default(input(tip_words + '[Y]/N: '), 'Y').upper()
        logging.debug(input_value)

    return input_value


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    # logging.info(input_default(input(), 'abc'))
    logging.info(input_pwd())
    # logging.info(input_checking_YN())

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
