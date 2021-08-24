#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dataframe_func.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

import pandas as pd
import pyexcel as pe
from typing import List


def records_to_df(
        records_list: List[dict], col_list_request: List[str] = [],
        to_file: str = '', excel_str_num: bool = True,
        not_in_dict: dict = {}, sample_num: int = 0):
    """Convert records from responses to pd.DataFrames

    Args:
        records_list: List[dict]
            a list of records to convert
        col_list_request: List[str], default []
            a list of colname to filter the converted dataframe
        to_file: str, optional, default ''
            the filepath of output file, can be .csv or .xlsx
        excel_str_num: bool, default True
            define the num type in output file, work only in excel file
        not_in_dict: dict, default {}
            a dicf to exclude some values from the converted dataframe

            For example, {'id': ['1111']} will exclude the value '1111' in col named 'id'
        sample_num: int, default 0
            return a sample dataframe with sample_num rows as the final result
    """
    log.info("len(records_list): %s", len(records_list))

    df_full = pd.DataFrame.from_records(records_list)
    df = df_full[col_list_request] if col_list_request else df_full
    for col_name, _ in not_in_dict.items():
        if col_name not in df.columns:
            not_in_dict.pop(col_name)
            log.warning('Invaild col_name[{}] in not_in_dict for dataframe. Abandoned it.'.format(col_name))

    df_filtered = df if not not_in_dict else df[[x not in col_list for col, col_list in not_in_dict.items() for x in df[col]]]
    log.info("len(df_filtered): %s", len(df_filtered))

    df_filtered_sampled = df_filtered.sample(n=sample_num) if sample_num else df_filtered
    log.info("len(df_filtered_sampled): %s", len(df_filtered_sampled))

    if to_file:
        df_to_file(df_filtered_sampled, to_file, excel_str_num)
    return df_filtered


def df_to_file(df: pd.DataFrame, to_file: str, excel_str_num: bool = True):
    """output df to a file

    Args:
        df: pd.DataFrame
            the dataframe to convert
        to_file: str
            the filepath of output file
        excel_str_num: bool, default True
            define the num type in output file, work only in excel file
    """
    if not isinstance(df, pd.DataFrame):
        log.debug('type(df): %s', type(df))
        log.error('The type of data inputed is not dataframe')
    else:
        if df.empty:
            log.error('The dataframe is blank')
        else:
            log.debug('df.head(5): %s', df.head(5))
            if not to_file:
                log.error('No filepath.')
            else:
                if to_file[::-1].find('.') != -1:
                    filetype = to_file[-int(to_file[::-1].find('.')):]
                    to_csvfile = to_file[:-int(to_file[::-1].find('.'))] + 'csv'
                    df.to_csv(to_csvfile, index=False, encoding='utf_8_sig')
                    if filetype in ('xls', 'xlsx'):
                        pe.save_as(
                            file_name=to_csvfile, dest_file_name=to_file,
                            encoding='utf_8_sig',
                            auto_detect_int=bool(1 - excel_str_num),
                            auto_detect_float=bool(1 - excel_str_num)
                        )
                        if Path(to_file).exists() and Path(to_csvfile).exists():
                            Path(to_csvfile).unlink()
                else:
                    log.error('Invaild filename[{}].'.format(to_file))


if __name__ == '__main__':
    import json

    # test list of records_to_df
    with open(cwdPath.joinpath('res\\pro\\response.txt'), encoding='utf-8') as f:
        data = json.loads(f.read())
    log.info(data['data']['records'][:3])
    df = pd.DataFrame.from_records(data['data']['records'])
    log.info(df[['id', 'status', 'subjectName', 'enableTypeName']].head(10))

    # test df_to_file
    import numpy as np
    rng = np.random.default_rng(0)
    df = pd.DataFrame(rng.random(100))
    df_to_file(df, 'D:\\to_file.xls', False)
    df_to_file(df, 'D:\\to_file.xlsx', True)
    df_to_file(df, 'D:\\to_file.csv')
