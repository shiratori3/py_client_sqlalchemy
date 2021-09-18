#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dataframe_func.py
@Author  :   Billy Zhou
@Time    :   2021/09/18
@Desc    :   None
'''


import sys
from pathlib import Path

cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

import datetime
import numpy as np
import pandas as pd
import pyexcel as pe
from typing import List
from functools import reduce
from operator import or_


def records_to_df(
        records_list: List[dict],
        col_list_request: List[str] = [], empty_str2nan: bool = True,
        to_file: str = '', excel_str_num: bool = True,
        row_in_col_to_capture: dict = {}, row_in_col_to_discard: dict = {},
        sample_num: int or float = 0,
        timestamp_to_datetime: dict = {}, utc_add: bool = True,):
    """Convert records from responses to pd.DataFrames

    Args:
    ----
        records_list: List[dict]
            a list of records to convert
        col_list_request: List[str], default []
            a list of colname to filter the converted dataframe
        empty_str2nan: bool, default True
            whether to convert empty string like '' or '\n' or ' ' to np.nan
        to_file: str, optional, default ''
            the filepath of output file, can be .csv or .xlsx
        excel_str_num: bool, default True
            define the num type in output file, work only in excel file
        row_in_col_to_capture: dict, default {}
        row_in_col_to_discard: dict, default {}
            a dict to filter rows in cols from the dataframe.
            diff cols will be combined by operator.or_
            a filter of string cols like '%row_string%' is accepted.

            For example,
            {'id': ['1111', '2222']} will include/exclude both of value '1111' and '2222' in col named 'id'
            {'id': ['%11%']} will include/exclude the string contains '11' in col named 'id'
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
    log.debug("df_full.columns: \n{}".format(df_full.columns))

    df = df_full[col_list_request] if col_list_request else df_full
    if empty_str2nan:
        # replace '' with np.NaN
        # \s matches any whitespace character (equivalent to [\r\n\t\f\v ])
        df = df.replace(r'^\s*$', np.NaN, regex=True)

    # filter the df according to the row_in_col_to_capture and row_in_col_to_discard
    df_filtered = df_filter_by_dict('include', df, row_in_col_to_capture)
    log.info("len of df_filtered_include: %s", len(df_filtered))
    df_filtered = df_filter_by_dict('exclude', df_filtered, row_in_col_to_discard)
    log.info("len of df_filtered_exclude: %s", len(df_filtered))

    # check the vaild of sample_num and get a sample from df
    sample_num = int(sample_num * len(df_filtered)) if sample_num < 1 and sample_num > 0 and isinstance(
        sample_num, float) else abs(int(sample_num))
    df_filtered_sampled = df_filtered.sample(n=sample_num) if sample_num and sample_num < len(df_filtered) else df_filtered
    log.info("len(df_filtered_sampled): %s", len(df_filtered_sampled))

    # check the vaild of timestamp_to_datetime and try to convert the type of cols in df
    for col_name, timestamp_unit in timestamp_to_datetime.items():
        if col_name not in df_filtered_sampled.columns:
            timestamp_to_datetime.pop(col_name)
            log.warning('Invaild col_name[{}] in timestamp_to_datetime for dataframe.'.format(
                col_name))
        else:
            try:
                df_filtered_sampled.loc[:, col_name] = pd.to_datetime(
                    df_filtered_sampled[col_name], unit=timestamp_unit)
                if utc_add:
                    df_filtered_sampled.loc[:, col_name] = df_filtered_sampled[
                        col_name] + pd.Timedelta(
                            datetime.datetime.now().astimezone().utcoffset())
            except Exception as e:
                log.error('An error occurred. {}'.format(e.args[-1]))

    if to_file:
        df_to_file(df_filtered_sampled, to_file, excel_str_num)
    return df_filtered


def dict_vaild_in_df(d_to_check: dict, df: pd.DataFrame) -> None:
    """check the vaild of dict for df"""
    pop_keys = []
    for col_name, row_values in d_to_check.items():
        if col_name not in df.columns:
            pop_keys.append(col_name)
            log.warning('col_name[{}] not in for dataframe.columns.'.format(
                col_name))
        if not row_values:
            pop_keys.append(col_name)
            log.warning('None value of col_name[{}] for dataframe.'.format(
                col_name))
    for key in pop_keys:
        d_to_check.pop(key)


def df_filter_by_dict(filter_type: str, df: pd.DataFrame, row_in_col_dict: dict) -> pd.DataFrame:
    """filter the df according to the row_in_col_dict

    Args:
    ----
        filter_type: str, {'include', 'exclude'}
            the type of filter
        df: pd.DataFrame
            the dataframe to filter
        row_in_col_dict: dict, default {}
            a dict to filter rows in cols from the dataframe.
            diff cols will be combined by operator.or_
            a filter of string cols like '%row_string%' is accepted.

            For example,
            {'id': ['1111', '2222']} will filter both of value '1111' and '2222' in col named 'id'
            {'id': ['%11%']} will filter the string contains '11' in col named 'id'
    """
    # check the vaild of filter_type
    if filter_type not in {'include', 'exclude'}:
        raise KeyError(f'Unvaild type {filter_type} for df_filter_by_dict')

    if not row_in_col_dict:
        return df
    else:
        # generate masks according to the row_in_col_dict
        null_mask = create_mask_from_dict('null', df, row_in_col_dict)
        log.debug("null_mask: \n{}".format(null_mask))
        contain_mask = create_mask_from_dict('contain', df, row_in_col_dict)
        log.debug("contain_mask: \n{}".format(contain_mask))

        # check row_in_col_dict before creating include_mask
        log.debug("row_in_col_dict before checked: {}".format(row_in_col_dict))
        dict_vaild_in_df(row_in_col_dict, df)
        log.debug("row_in_col_dict after checked: {}".format(row_in_col_dict))
        include_mask = pd.Series(
            [row_value in row_values for col_name, row_values in row_in_col_dict.items() for row_value in df[col_name]],
            dtype=object
        )
        log.debug("include_mask: \n{}".format(include_mask))

        # combine masks to mask
        mask = null_mask if not null_mask.empty else pd.Series([], dtype=object)
        log.debug("masks: \n{}".format(pd.concat([mask, null_mask], axis=1)))
        mask = mask | contain_mask if not contain_mask.empty and not mask.empty else contain_mask if not contain_mask.empty else mask
        log.debug("masks: \n{}".format(pd.concat([mask, null_mask, contain_mask], axis=1)))
        mask = mask | include_mask if not include_mask.empty and not mask.empty else include_mask if not include_mask.empty else mask
        log.debug("masks: \n{}".format(pd.concat([mask, null_mask, contain_mask, include_mask], axis=1)))
        if isinstance(mask, pd.Series):
            mask = mask.astype(bool)
        if filter_type == 'exclude':
            mask = ~mask
            log.debug("mask: \n{}".format(mask))
            log.debug("masks: \n{}".format(pd.concat([mask, ~mask], axis=1)))

        # filter df with the mask
        return df if mask.empty else df.loc[mask]


def create_mask_from_dict(mask_type: str, df: pd.DataFrame, row_in_col_dict: dict) -> pd.Series:
    """generate masks according to df and row_in_col_dict

    Args:
        mask_type: str, {'null', 'contain'}
            the type of masks
        df: pd.DataFrame
            the df to use mask later
        row_in_col_dict: dict
            a dict to tell whether to generate masks.
            diff masks will be combined by operator.or_
            a filter of string cols like '%row_string%' is accepted.

            For example,
            {'id1': ['']} will create a mask of null value in col named 'id1'
            {'id2': ['%11%']} will create a mask of row contains '11' in col named 'id2'

    Return:
    ------
        mask: pd.Series
            a pd.Series without name which combines all mask with or_
    """
    # generate masks for row_in_col_dict
    masks = []
    for col_name, row_values in row_in_col_dict.items():
        if mask_type == 'null':
            if '' in row_values:
                row_in_col_dict[col_name].remove('')
                mask = df[col_name].isnull()
                log.debug("df[col_name].isnull(): \n{}".format(mask))
                masks.append(mask)
        elif mask_type == 'contain':
            for row_value in row_values:
                if isinstance(row_value, str) and len(row_value) > 2:
                    if '%' in row_value and row_value[0] == row_value[-1] == '%':
                        row_in_col_dict[col_name].remove(row_value)
                        log.debug("row_value[1:-1]: {}".format(row_value[1:-1]))
                        mask = df[col_name].str.contains(row_value[1:-1])
                        log.debug(f"df[{col_name}].str.contains(row_value[1:-1]): \n{mask}")
                        masks.append(mask)
        else:
            raise KeyError(f'invaild input {mask_type} for create_mask_from_dict')
    return reduce(or_, masks) if masks else pd.Series([], dtype=object)


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

    if True:
        # test records_to_df
        with open(cwdPath.joinpath('res\\pro\\response.txt'), encoding='utf-8') as f:
            data = json.loads(f.read())
        log.info(data['data']['records'][:1])
        df = pd.DataFrame.from_records(data['data']['records'])
        log.info("df.head(15): \n{}".format(
            df[['id', 'status', 'subjectName', 'enableTypeName']].head(15)))

    if False:
        # test create_mask_from_dict
        row_in_col_dict = {
            'id': ['%13%'],
            'subjectName': ['%#%', '供应商与客户_主要供应商', '供应商与客户_主要客户'],
            'pdfId': [''],
        }
        contain_mask = create_mask_from_dict('contain', df, row_in_col_dict)
        log.debug("contain_mask: \n{}".format(pd.concat([contain_mask, df['id'], df['subjectName']], axis=1)))

        df = df.replace(r'^\s*$', np.NaN, regex=True)  # replace '' with np.NaN
        null_mask = create_mask_from_dict('null', df, row_in_col_dict)
        log.debug("null_mask: \n{}".format(pd.concat([null_mask, df['pdfId']], axis=1)))

    if False:
        # test df_filter_by_dict
        row_in_col_dict = {
            'id': ['%13%'],
            'subjectName': ['%#%', '供应商与客户_主要供应商', '供应商与客户_主要客户'],
            'pdfId': [''],
        }
        filter_type = 'include' if False else 'exclude'

        df_filtered = df_filter_by_dict(filter_type, df, row_in_col_dict)
        log.debug("df_filtered: \n{}".format(pd.concat([
            df_filtered['id'], df_filtered['subjectName'], df_filtered['pdfId']], axis=1)))

    if False:
        # test df_to_file
        import numpy as np
        rng = np.random.default_rng(0)
        df = pd.DataFrame(rng.random(100))
        df_to_file(df, 'D:\\to_file.xls', False)
        df_to_file(df, 'D:\\to_file.xlsx', True)
        df_to_file(df, 'D:\\to_file.csv')
