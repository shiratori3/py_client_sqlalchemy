#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ErrorWordTemplate.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.Logger import logger  # noqa: E402
log = logger.get_logger(__name__)

from src.manager.main import conf  # noqa: E402
from src.basic.sql_func import sql_read  # noqa: E402


class SqlTemplate:
    def __init__(
            self,
            temp_folder: Path = Path(conf.conf_dict['path']['confpath']).joinpath('res\\dev\\sql_template'),
            sql_folder: Path = Path(conf.conf_dict['path']['confpath']).joinpath('res\\dev\\sqlscript')
    ) -> None:
        self.temp_folder = Path(temp_folder)
        self.sql_folder = Path(sql_folder)
        if not self.temp_folder.exists:
            self.temp_folder.mkdir(parents=True)
        if not self.sql_folder.exists:
            self.sql_folder.mkdir(parents=True)
        self.sql_result = ''

    def read_template(self, temp_fname):
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
        # rewrite this function by yourself
        self.sql_result = "SELECT 'sql_template'"


if __name__ == '__main__':
    sql_temp = SqlTemplate()
    sql_temp.sql_folder = sql_temp.sql_folder.joinpath('error_word')
    print(sql_temp.sql_folder)

    sql_temp.read_template('error_word_L.sql')
    print(sql_temp.sql_temp)
    sql_temp.create_sql()
    sql_temp.save_sql('save_test.sql')
