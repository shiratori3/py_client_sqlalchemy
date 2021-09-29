#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sql_func.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr
log = logmgr.get_logger(__name__)

import pandas as pd
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy.engine import Engine
from sqlalchemy.sql.elements import TextClause
from src.basic.dataframe_func import df_to_file


def sql_read(script_file: Path or str, encoding='utf8'):
    """read .sql file from script_file"""
    try:
        sql = ''
        with open(script_file, encoding=encoding) as f:
            for line in f.readlines():
                sql = sql + line
        log.debug('plaintext in sql: %s', sql)
        return sql
    except Exception as e:
        log.error("An error occurred. {}".format(e.args[-1]))


def sql_query(
        engine: Engine, sql: str, sql_db_switch: str = '',
        commit_after: bool = False, params_dict: dict = '',
        fetchall: bool = True, return_df: bool = True,
        to_file: str or Path = '', excel_str_num: bool = True):
    """execute a sql query to engine

    Args:
        engine: sqlalchemy.engine.Engine
            a instance of sqlalchemy.engine.Engine
        sql: str
            the sql script to query
        sql_db_switch: str, default ''
            a simple sql script to swtich using db, such as 'USE information_schema' for MySQL
        bindparams: dict, default {}
            a dict of params for binding to sql
        commit_after: bool, default False
            whether to commit after execute
        fetchall: bool, default True
            whether to fetchall, if false, return fetchone
        return_df: bool, default True
            return original row or dataframe
        to_file: str or Path, default ''
            convert the result to dataframe and save to file
        excel_str_num: bool, default True
            define the num type in output file, work only in excel file
    """
    try:
        with engine.connect() as conn:
            if sql_db_switch:
                conn.execute(text(sql_db_switch))
            stmt = sql if isinstance(sql, TextClause) else text(sql)
            if params_dict:
                for key, value in params_dict.items():
                    expand = True if isinstance(value, list) else False
                    stmt = stmt.bindparams(bindparam(key, expanding=expand))
            log.debug("stmt: %s", stmt.compile(compile_kwargs={"literal_binds": True}))
            result = conn.execute(stmt, params_dict) if params_dict else conn.execute(stmt)
            # result.keys()  # result.RMKeyView, list-like object
            # result.all()  # list of tuple, same to fetchall()
            # result.fetchmany(size=2)  # list of one tuple
            # result.fetchone()  # tuple
            # result.fetchone()._asdict()  # dict
            if commit_after:
                conn.commit()
            else:
                row = result.fetchall() if fetchall else result.fetchone()
                log.debug("row: %s", row)

                if return_df or to_file:
                    df = pd.DataFrame(row, columns=list(result.keys()))
                    if to_file:
                        df_to_file(df, to_file, excel_str_num)

                return df if return_df else row
    except Exception as e:
        log.error("An error occurred. {}".format(e.args[-1]))
        if 'conn' in dir():
            conn.close()


if __name__ == '__main__':
    from src.manager.EngineManager import EngineManager  # noqa: E402

    manager = EngineManager()

    # testing sql_query
    manager.set_engine('mysql_local', future=True)
    engine_mssql = manager.get_engine('mysql_local')
    # no params
    sql = 'SELECT * FROM count_uncheck WHERE DATE(time_create) = "2021/08/10" and `all` > 300'
    sql_result = sql_query(
        engine_mssql, sql=sql, sql_db_switch='USE sys', return_df=True)
    log.info(sql_result)

    # with params
    sql = 'SELECT * FROM count_uncheck WHERE DATE(time_create) in :dates and `all` > :all_nums'
    params = {'dates': ['2021/08/10', '2021/08/11', '2021/08/12'], 'all_nums': 350}
    sql_result = sql_query(
        engine_mssql, sql=sql, sql_db_switch='USE sys', params_dict=params, return_df=True)
    log.info(sql_result)

    # testing sql_read
    manager.set_engine('164', future=True)
    engine_164 = manager.get_engine('164')
    sql = sql_read(cwdPath.joinpath('res\\dev\\sqlscript\\test_year.txt'))
    outfile = 'D:\\test.xlsx'
    sql_result = sql_query(
        engine_164, sql=sql, sql_db_switch='USE JYFIN', return_df=False, to_file=outfile)
    log.info(sql_result)
