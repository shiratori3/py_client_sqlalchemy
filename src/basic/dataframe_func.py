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

import datetime
import pandas as pd
import pyexcel as pe
from typing import List


def records_to_df(
        records_list: List[dict], col_list_request: List[str] = [],
        to_file: str = '', excel_str_num: bool = True,
        row_in_col_to_discard: dict = {}, sample_num: int or float = 0,
        timestamp_to_datetime: dict = {}, utc_add: bool = True):
    """Convert records from responses to pd.DataFrames

    Args:
    ----
        records_list: List[dict]
            a list of records to convert
        col_list_request: List[str], default []
            a list of colname to filter the converted dataframe
        to_file: str, optional, default ''
            the filepath of output file, can be .csv or .xlsx
        excel_str_num: bool, default True
            define the num type in output file, work only in excel file
        row_in_col_to_discard: dict, default {}
            a dicf to exclude some rows in cols from the converted dataframe

            For example, {'id': ['1111']} will exclude the value '1111' in col named 'id'
        sample_num: int or float, default 0
            return a sample dataframe with sample_num rows as the final result.
            When type of sample_num is float and value less than 1 which meaning a percent,
            cal sample_num = int(sample_num * len(df_filtered))
        timestamp_to_datetime: dict, default {}
            a dict to convert timestamp data in cols in the converted dataframe

            For example, {'lastModifiedDate': 'ms'} will convert the timestamps
            in col named 'lastModifiedDate' with pd.to_datetime(unit='ms')
        utc_add: bool, default True
            whether add the timedelta between localtime and utc when convert timestamp
    """
    log.info("len(records_list): %s", len(records_list))

    # convert reords to df and filter the df with col_list_request
    df_full = pd.DataFrame.from_records(records_list)
    df = df_full[col_list_request] if col_list_request else df_full

    # check the vaild of keys in row_in_col_to_discard and filter the df with row_in_col_to_discard
    for col_name in row_in_col_to_discard.keys():
        if col_name not in df.columns:
            row_in_col_to_discard.pop(col_name)
            log.warning('Invaild col_name[{}] in row_in_col_to_discard for dataframe.'.format(
                col_name))
    df_filtered = df if not row_in_col_to_discard else df[[
        x not in col_list for col, col_list in row_in_col_to_discard.items() for x in df[col]]]
    log.info("len(df_filtered): %s", len(df_filtered))

    # check the vaild of sample_num and get a sample from df
    sample_num = int(sample_num * len(df_filtered)) if sample_num < 1 and sample_num > 0 and isinstance(
        sample_num, float) else abs(int(sample_num))
    df_filtered_sampled = df_filtered.sample(n=sample_num) if sample_num else df_filtered
    log.info("len(df_filtered_sampled): %s", len(df_filtered_sampled))

    # check the vaild of timestamp_to_datetime and try to convert the type of cols in df
    for col_name, timestamp_unit in timestamp_to_datetime.items():
        if col_name not in df_filtered_sampled.columns:
            timestamp_to_datetime.pop(col_name)
            log.warning('Invaild col_name[{}] in timestamp_to_datetime for dataframe.'.format(
                col_name))
        else:
            try:
                df_filtered_sampled[col_name] = pd.to_datetime(
                    df_filtered_sampled[col_name], unit=timestamp_unit)
                if utc_add:
                    df_filtered_sampled[col_name] = df_filtered_sampled[
                        col_name] + pd.Timedelta(
                            datetime.datetime.now().astimezone().utcoffset())
            except Exception as e:
                log.error('An error occurred. {}'.format(e.args[-1]))

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
