#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   input_check.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import getpass


def input_default(default_word='', tip_words='Please input words.'):
    input_data = input(tip_words + '(default: ' + default_word + ')\n')
    if input_data.strip() == '':
        print('Blank input. Using the default value: {0}'.format(default_word))
        return default_word
    else:
        return input_data


def input_pwd(tip_words='Please input your password:'):
    return getpass.getpass(tip_words)


def input_checking_list(
        input_list,
        tip_words='Please input words.', case_sens=False,
        min_num=0, default_list=['Y', 'N']):
    input_list_str = ''
    if not (type(input_list) == list and len(input_list) > min_num):
        default_list_str = str(default_list)
        print('Invaild input list. Using the default list of ' + default_list_str + '.')
        input_list = default_list

    for num, value in enumerate(input_list):
        if num == 0:
            input_list_str = '[' + value + ']'
            default_value = value
        else:
            input_list_str = input_list_str + '/' + value
    tip_words = tip_words + '(' + input_list_str + '): '

    if case_sens:
        input_value = input_default(default_value, tip_words)
        while not (set([input_value]) & set(input_list)):
            print('Unexpect input! Please input words in ' + input_list_str + '.')
            input_value = input_default(default_value, tip_words)
    else:
        input_value = input_default(default_value.upper(), tip_words).upper()
        while not (set([input_value]) & set([i.upper() for i in input_list])):
            print('Unexpect input! Please input words in ' + input_list_str + '.')
            input_value = input_default(default_value.upper(), tip_words).upper()

    return input_value


def input_checking_YN(tip_words='Please input words.', default_Y=True):
    input_list = ['Y', 'N']
    if not default_Y:
        input_list = ['N', 'Y']
    return input_checking_list(input_list, tip_words, case_sens=False)


if __name__ == "__main__":
    import logging

    logging.info("return : {}".format(input_default('abc')))
    logging.info("return : {}".format(input_pwd()))
    logging.info("return : {}".format(input_checking_YN()))
    logging.info("return : {}".format(input_checking_list(['a', 'b', 'c', 'd'])))
    logging.info("return : {}".format(input_checking_list(['a'])))
    logging.info("return : {}".format(input_checking_list([])))
    logging.info("return : {}".format(input_checking_list('a')))
