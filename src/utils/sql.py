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

import time
import datetime
import pandas as pd
from IPython.display import display
from sqlalchemy import text
from sqlalchemy import bindparam
from sqlalchemy.engine import Engine
from sqlalchemy.sql.elements import TextClause
from src.utils.dataframe import df_to_file


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


def sql_result_output(
        engine: Engine, sql: str, sql_db_switch: str = '',
        distinct_result: bool = False, show_max_row: int = 30,
        overflow_to_file: bool = True, overflow_filepath: Path = '',
        show_runtime: bool = True, df_styler: bool = True):
    """execute a sql query to engine

    Args:
        engine: sqlalchemy.engine.Engine
            a instance of sqlalchemy.engine.Engine
        sql: str
            the sql script to query
        sql_db_switch: str, default ''
            a simple sql script to swtich using db, such as 'USE information_schema' for MySQL
        distinct_result: bool, default False
            whether to drop duplicate rows in result
        show_max_row: int, default 30
            the max num of row to output
        overflow_to_file: bool, default True
            whether to out the overflow result to file
        show_runtime: bool, default True
            whether to the run time of sql
        df_styler: bool, default True
            whether to use the styler to output the df result.
            if styler is used, the result will not be recored in log files.
    """
    log.info("Start to run sql. Waiting for result......")
    s_time = time.time()
    sql_result = sql_query(engine, sql, sql_db_switch=sql_db_switch, return_df=True)
    e_time = time.time()
    if show_runtime:
        log.info("run_time: {:.2f}s".format(e_time - s_time))

    # output the info of result
    if sql_result.empty:
        log.warning("SQL查询结果为空，请检查语句或输入参数。")
    else:
        log.info("row_num:  {!r}".format(sql_result.shape[0]))
        if distinct_result:
            sql_result = sql_result.drop_duplicates()
            log.info("distinct row_num:  {!r}".format(sql_result.shape[0]))
        # output the result
        if df_styler:
            display(sql_result.head(show_max_row).style.set_properties(**{'text-align': 'left'}))
        else:
            log.info("sql_result.head({0}): \n{1!r}".format(
                show_max_row, sql_result.head(show_max_row)))
        if sql_result.shape[0] > show_max_row:
            log.warning(f"SQL查询结果条数较多，未能全部显示，仅展示前{show_max_row}条")
            if overflow_to_file:
                overflow_filepath = cwdPath.joinpath('bin') \
                    if not overflow_filepath else Path(overflow_filepath)
                if overflow_filepath.exists():
                    overflow_filepath = str(overflow_filepath.joinpath(
                        "sql_{timestamp}.xlsx".format(
                            timestamp=datetime.datetime.now().strftime("%m%d%H%M%S%f")
                        )))
                    log.info(f'overflow result is output to file[{overflow_filepath}]')
                    df_to_file(sql_result, overflow_filepath)
                else:
                    log.error("invaild path[{}] to output the overflow sql result".format(
                        overflow_filepath))
        log.info("Result output end.")


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
