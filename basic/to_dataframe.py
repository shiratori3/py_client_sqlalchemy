#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   to_dataframe.py
@Author  :   Billy Zhou
@Time    :   2021/08/04
@Version :   1.4.0
@Desc    :   None
'''


import sys
import logging
import pandas as pd
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from basic.to_file import df_to_file  # noqa: E402


def list_of_dicts_to_df(records_list, col_list_request=[], num_to_str=True, to_file='', not_in_dict={}):
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
    for col_name, value_list in not_in_dict.items():
        if col_name not in df.columns:
            not_in_dict.pop(col_name)
            logging.info('Error col_name in not_in_dict for dataframe')

    df_filtered = df[[x not in col_list for col, col_list in not_in_dict.items() for x in df[col]]]

    if to_file:
        df_to_file(df_filtered, to_file, num_to_str)
    return df_filtered


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        # filename=os.path.basename(__file__) + '_' + time.strftime('%Y%m%d', time.localtime()) + '.log',
        # filemode='a',
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
