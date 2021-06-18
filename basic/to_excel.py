#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   to_excel.py
@Author  :   Billy Zhou
@Time    :   2021/06/01
@Version :   1.0.0
@Desc    :   None
'''


import logging
import pandas as pd
import pyexcel as pe
from pathlib import Path


def df_to_excel(df, to_file, num_to_str=True):
    if not isinstance(df, pd.DataFrame):
        logging.error('The type of data inputed is not dataframe')
        if df.empty:
            logging.error('The dataframe is blank')
        else:
            if not to_file:
                logging.error('Not to_file.')
            else:
                if to_file[::-1].find('.') != -1:
                    to_filetype = to_file[-int(to_file[::-1].find('.')):]
                    to_csvfile = to_file[:-int(to_file[::-1].find('.'))] + 'csv'
                    df.to_csv(to_csvfile, index=False, encoding='utf_8_sig')
                    # to_file = 'D:\\test_todf.xls'
                    if to_filetype in ('xls', 'xlsx'):
                        pe.save_as(
                            file_name=to_csvfile, dest_file_name=to_file,
                            encoding='utf_8_sig',
                            auto_detect_int=bool(1 - num_to_str),
                            auto_detect_float=bool(1 - num_to_str)
                        )
                        if Path(to_file).exists() and Path(to_csvfile).exists():
                            Path(to_csvfile).unlink()


def list_of_dicts_to_df(records_list, col_list_request=[], num_to_str=True, to_file=''):
    records_array = []
    col_list = []
    col_num_list = []
    for i, key in enumerate(records_list[0].keys()):
        if col_list_request:
            if key in col_list_request:
                col_list.append(key)
                col_num_list.append(i)
        else:
            col_list.append(key)
    records_array.append(col_list)

    for record_dict in records_list:
        value_list = []
        for i, value in enumerate(record_dict.values()):
            if col_list_request:
                if i in col_num_list:
                    value_list.append(value)
            else:
                value_list.append(value)
        records_array.append(value_list)

    df = pd.DataFrame(records_array[1:], columns=records_array[0])

    if to_file:
        df_to_excel(df, to_file, num_to_str)
    return df


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
