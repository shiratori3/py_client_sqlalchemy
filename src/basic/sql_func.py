#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sql_func.py
@Author  :   Billy Zhou
@Time    :   2021/08/06
@Version :   1.5.0
@Desc    :   None
'''


import sys
import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy.sql.elements import TextClause
sys.path.append(str(Path(__file__).parents[2]))

from src.basic.dataframe_func import df_to_file  # noqa: E402


def sql_read(script_file, encoding='utf8'):
    try:
        sql = ''
        with open(str(script_file), encoding=encoding) as f:
            for line in f.readlines():
                sql = sql + line
        logging.debug('plaintext: %s', sql)
        return sql
    except Exception as e:
        logging.debug("An error occurred. {}".format(e.args[-1]))


def sql_query(
        engine, sql, sql_db_switch='',
        bindparams={}, commit_after=False,
        fetchall=True, return_df=True, to_file='', excel_str_num=True):
    try:
        with engine.connect() as conn:
            if sql_db_switch:
                conn.execute(text(sql_db_switch))
            if isinstance(sql, TextClause):
                stmt = sql
            else:
                if bindparams:
                    stmt = text(sql)
                    for bind_key, params in bindparams.items():
                        logging.debug("bindparams[{0}]: {1}".format(bind_key, params))
                        for key, value in params.items():
                            if key == 'value':
                                stmt = stmt.bindparams(bindparam(bind_key, value=value))
                            # elif key == 'type_':
                            #     stmt = stmt.bindparams(bindparam(bind_key, type_=value))
                            # elif key == 'unique':
                            #     stmt = stmt.bindparams(bindparam(bind_key, unique=value))
                else:
                    stmt = text(sql)
            logging.debug("stmt: %s", stmt.compile(compile_kwargs={"literal_binds": True}))
            result = conn.execute(stmt)
            # result.keys()  # result.RMKeyView, list-like object
            # result.all()  # list of tuple, same to fetchall()
            # result.fetchmany(size=2)  # list of one tuple
            # result.fetchone()  # tuple
            # result.fetchone()._asdict()  # dict
            if commit_after:
                conn.commit()
            else:
                row = result.fetchall() if fetchall else result.fetchone()
                logging.debug("row: %s", row)

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

    from src.manager.ConfManager import cwdPath  # noqa: E402
    from src.manager.EngineManager import EngineManager  # noqa: E402

    manager = EngineManager()
    manager.set_engine('164', future=True)
    engine_164 = manager.get_engine('164')

    # testing sql_read and sql_query
    sql = sql_read(cwdPath.joinpath('res\\dev\\test_year.txt'))
    outfile = 'D:\\test.xlsx'
    sql_result = sql_query(
        engine_164, sql=sql, sql_db_switch='USE JYFIN', return_df=False, to_file=outfile)
    logging.info(sql_result)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
