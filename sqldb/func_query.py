#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_query.py
@Author  :   Billy Zhou
@Time    :   2021/03/12
@Version :   1.0.0
@Desc    :   None
'''


import sys
import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import text
sys.path.append(str(Path(__file__).parent.parent))

from sqldb.func_basic import sql_read  # noqa: E402
from basic.to_excel import df_to_file  # noqa: E402


def sql_query(
        engine, sql,
        sql_db_switch='', fetchall=True, return_df=True, to_file='', excel_str_num=True):
    try:
        with engine.connect() as conn:
            if sql_db_switch:
                conn.execute(text(sql_db_switch))
            result = conn.execute(text(sql))
            # result.keys()  # result.RMKeyView, list-like object
            # result.all()  # list of tuple, same to fetchall()
            # result.fetchmany(size=2)  # list of one tuple
            # result.fetchone()  # tuple
            # result.fetchone()._asdict()  # dict
            row = result.fetchall() if fetchall else result.fetchone()

            if return_df or to_file:
                df = pd.DataFrame(row, columns=list(result.keys()))
                if to_file:
                    df_to_file(df, to_file, excel_str_num)

            return df if return_df else row
    except Exception as e:
        logging.debug("An error occurred. {}".format(e.args[-1]))
        if 'conn' in dir():
            conn.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    from sqldb.init_db import SqlDbManager
    from conf_manage import readConf  # noqa: E402
    cwdPath = Path(readConf()["path"]['cwd'])

    manager = SqlDbManager()
    manager.set_engine('164', future=True)
    engine_164 = manager.get_engine('164')

    sql = sql_read(cwdPath.joinpath(
        'gitignore\\sqlscript\\数值异常：首列均为年份数开头.txt'))
    outfile = 'D:\\test.xlsx'
    sql_result = sql_query(
        engine_164, sql=sql, sql_db_switch='USE JYFIN', return_df=False, to_file=outfile)
    logging.info(sql_result)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
