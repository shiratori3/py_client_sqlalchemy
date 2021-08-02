#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   init_db.py
@Author  :   Billy Zhou
@Time    :   2021/07/30
@Version :   1.3.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
from sqlalchemy import engine_from_config
from sqlalchemy import text
sys.path.append(str(Path(__file__).parents[1]))

from ConnUI import FileManager  # noqa: E402
from ConnUI import ConnUI  # noqa: E402


class SqlDbManager(object):
    def __init__(self, conn_ui=False):
        self._engine_dict = {}
        if not conn_ui:
            self.CUI = ConnUI(FileManager(file_encrypt=True, pubkeyfile=None, prikeyfile=None))
        else:
            # use the inputed CUI
            self.CUI = conn_ui

    def run_CUI(self, inputed_code='', conn_name=''):
        self.CUI.run()

    def read_conn_list(self):
        conn_list = [name for name, path in self.CUI.fmgr.read_conf()['conn'].items()]
        logging.info(
            'Existed connections: %s', '"' + '",  "'.join(conn_list) + '"')

    def test_engine(self, engine):
        # engine test
        with engine.connect() as conn:
            result = conn.execute(text("select 'Testing engine.'"))
            if result.scalar():
                logging.info('Connect succeed.')
                return True
            else:
                return False

    def set_engine(self, conn_name, try_max=3, **kwargs):
        try_time = 0
        failed = False
        self._engine_dict[conn_name] = ''
        while not self._engine_dict[conn_name] and try_time <= try_max:
            try:
                if failed:
                    logging.info('Login failed.')
                try_time += 1
                conf_dict = self.CUI.run('READ', conn_name)
                if conf_dict:
                    if 'pyodbc' in conf_dict['sqlalchemy.url']:
                        # depend your native version
                        conf_dict['sqlalchemy.url'] += '?driver=SQL+Server+Native+Client+11.0'

                    # add kwargs to conf_dict
                    if kwargs:
                        logging.info("engine additional kwargs: %s", kwargs)
                        for key, value in kwargs.items():
                            conf_dict['sqlalchemy.' + key] = value
                    logging.debug("conf_dict with kwargs: %s", conf_dict)
                    self._engine_dict[conn_name] = engine_from_config(conf_dict, prefix='sqlalchemy.')
                    self.test_engine(self._engine_dict[conn_name])
                failed = True
            except Exception as e:
                logging.debug("An error occurred. {!r}".format(e.args[-1]))
            finally:
                if try_time > try_max:
                    logging.error('Login failed too much time. Stop trying.')

    def get_engine(self, conn_name):
        if self._engine_dict.get(conn_name):
            if self.test_engine(self._engine_dict[conn_name]):
                return self._engine_dict[conn_name]
            else:
                logging.warning(
                    "The engine[{0}] connect failed. Drop it.".format(conn_name))
                self._engine_dict.pop(conn_name)
        else:
            logging.warning("The engine[{0}] is not found.".format(conn_name))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    manager = SqlDbManager()
    manager.read_conn_list()
    manager.set_engine('164', future=True)
    engine_164 = manager.get_engine('164')
    # print(manager._engine_dict)
    # manager.run_CUI()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
