#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   SqlTemplate.py
@Author  :   Billy Zhou
@Time    :   2021/08/22
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

from src.utils.sql import sql_read  # noqa: E402


class SqlTemplate:
    """Create sql script from sql_template script

    Attrs:
        temp_folder: Path, default cwdPath.joinpath('res\\dev\\sql_template')
            the directory save the sql_template script
        sql_folder: Path, default cwdPath.joinpath('res\\dev\\sqlscript')
            the directory to save the sql script created from sql_template script
        sql_temp: str
            sql_template script readed from read_template(temp_fname)
        sql_result: str
            sql script created by create_sql() from sql_template script

    Methods:
        read_template(self, temp_fname):
            read sql_temp from Path(self.temp_folder).joinpath(temp_fname)
        save_sql(self, sql_fname: str):
            save sql_result to Path(self.sql_folder).joinpath(sql_fname)
        create_sql(self):
            create sql_result from sql_temp
    """
    def __init__(
            self,
            temp_folder: Path = cwdPath.joinpath('res\\dev\\sql_template'),
            sql_folder: Path = cwdPath.joinpath('res\\dev\\sqlscript')
    ) -> None:
        self.temp_folder = Path(temp_folder)
        self.sql_folder = Path(sql_folder)
        if not self.temp_folder.exists:
            self.temp_folder.mkdir(parents=True)
        if not self.sql_folder.exists:
            self.sql_folder.mkdir(parents=True)
        self.sql_result = ''

    def read_template(self, temp_fname: str):
        """read sql_temp from Path(self.temp_folder).joinpath(temp_fname)"""
        if not Path(self.temp_folder).exists():
            raise ValueError('{} is not a vaild filepath.'.format(self.temp_folder))
        else:
            fpath = Path(self.temp_folder).joinpath(temp_fname)
            if not Path(fpath).exists():
                raise ValueError('{} is not a vaild filepath.'.format(fpath))
            else:
                self.sql_temp = sql_read(fpath)
                log.debug("self.sql_temp: {!r}".format(self.sql_temp))
                return self.sql_temp

    def save_sql(self, sql_fname: str):
        """save sql_result to Path(self.sql_folder).joinpath(sql_fname)"""
        if not self.sql_result:
            raise ValueError('sql_result is blank')
        else:
            if not Path(self.sql_folder).exists():
                raise ValueError('{} is not a vaild filepath.'.format(self.sql_folder))
            else:
                fpath = Path(self.sql_folder).joinpath(sql_fname)
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(self.sql_result)

    def create_sql(self) -> None:
        """create sql_result from sql_temp

        you should rewrite this method by yourself"""
        self.sql_result = "SELECT 'sql_template'"


if __name__ == '__main__':
    sql_temp = SqlTemplate()
    sql_temp.sql_folder = sql_temp.sql_folder.joinpath('error_word')
    print(sql_temp.sql_folder)

    sql_temp.read_template('error_word_L.sql')
    print(sql_temp.sql_temp)
    sql_temp.create_sql()
    sql_temp.save_sql('save_test.sql')
