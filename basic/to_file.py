#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   to_file.py
@Author  :   Billy Zhou
@Time    :   2021/08/04
@Version :   1.4.0
@Desc    :   None
'''


import logging
import pandas as pd
import pyexcel as pe
from pathlib import Path


def df_to_file(df, to_file, num_to_str=True):
    logging.debug('df.head: %s', df.head())
    logging.debug('type(df): %s', type(df))
    logging.debug('to_file: %s', to_file)
    if not isinstance(df, pd.DataFrame):
        logging.error('The type of data inputed is not dataframe')
    else:
        if df.empty:
            logging.error('The dataframe is blank')
        else:
            if not to_file:
                logging.error('No filepath.')
            else:
                if to_file[::-1].find('.') != -1:
                    filetype = to_file[-int(to_file[::-1].find('.')):]
                    to_csvfile = to_file[:-int(to_file[::-1].find('.'))] + 'csv'
                    df.to_csv(to_csvfile, index=False, encoding='utf_8_sig')
                    if filetype in ('xls', 'xlsx'):
                        pe.save_as(
                            file_name=to_csvfile, dest_file_name=to_file,
                            encoding='utf_8_sig',
                            auto_detect_int=bool(1 - num_to_str),
                            auto_detect_float=bool(1 - num_to_str)
                        )
                        if Path(to_file).exists() and Path(to_csvfile).exists():
                            Path(to_csvfile).unlink()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    import numpy as np
    rng = np.random.default_rng(0)
    df = pd.DataFrame(rng.random(100))
    df_to_file(df, 'D:\\to_file.csv')
    df_to_file(df, 'D:\\to_file.xls', False)
    df_to_file(df, 'D:\\to_file.xlsx', True)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
