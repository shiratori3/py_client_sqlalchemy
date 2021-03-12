#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   input_check.py
@Author  :   Billy Zhou
@Time    :   2021/03/01
@Version :   1.1.0
@Desc    :   None
'''


import logging

import msvcrt


def input_default(input_data, default_word=''):
    if input_data.strip() == '':
        print('Blank input. Using the default value: {0}'.format(default_word))
        return default_word
    else:
        return input_data


def input_pwd(tip_words='Please input your password:'):
    chars = []

    print(tip_words)

    while True:

        try:
            newChar = msvcrt.getch().decode(encoding="utf-8")
        except Exception as e:
            logging.debug("error: %s", e)
            return input("你很可能不是在cmd命令行下运行，密码输入将不能隐藏:")
        if newChar in '\r\n':  # 如果是换行，则输入结束
            logging.debug("your password is:{0}\n".format(''.join(chars)))
            break
        elif newChar == '\b':  # 如果是退格，则删除密码末尾一位并且删除一个星号
            if chars:
                del chars[-1]
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格
                msvcrt.putch(' '.encode(encoding='utf-8'))  # 输出一个空格覆盖原来的星号
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格准备接受新的输入
        else:
            chars.append(newChar)
            msvcrt.putch('*'.encode(encoding='utf-8'))  # 显示为星号

    print("\nInput end.")
    return (''.join(chars))


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
    # logging.info(input_pwd())
    logging.info(input_checking_YN())

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
