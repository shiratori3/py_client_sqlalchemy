#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ErrorWordTemplate.py
@Author  :   Billy Zhou
@Time    :   2021/08/18
@Version :   1.0.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2]))

from src.manager.ConfManager import conf  # noqa: E402
from src.basic.sql_func import sql_read  # noqa: E402


class SqlTemplate:
    def __init__(
            self,
            temp_folder: Path = Path(conf.conf_dict['path']['confpath']).joinpath('docs\\sql_template'),
            sql_folder: Path = Path(conf.conf_dict['path']['confpath']).joinpath('docs\\sqlscript')
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
                logging.debug("self.sql_temp: {!r}".format(self.sql_temp))
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
    logging.basicConfig(
        level=logging.INFO,
        # filename=os.path.basename(__file__) + '_' + time.strftime('%Y%m%d', time.localtime()) + '.log',
        # filemode='a',
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    sql_temp = SqlTemplate()
    sql_temp.sql_folder = sql_temp.sql_folder.joinpath('error_word')
    print(sql_temp.sql_folder)

    sql_temp.read_template('error_word_L.sql')
    print(sql_temp.sql_temp)
    sql_temp.create_sql()
    sql_temp.save_sql('save_test.sql')

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
