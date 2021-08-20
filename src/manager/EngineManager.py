#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   EngineManager.py
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

from sqlalchemy import engine_from_config
from sqlalchemy import text
from src.manager.ConnManager import ConnManager  # noqa: E402
from src.manager.ConnManager import ConnManagerUI  # noqa: E402


class EngineManager(object):
    def __init__(self, cmgr_ui: ConnManagerUI(ConnManager) = None):
        self._engine_dict = {}
        self.cmgr_ui = cmgr_ui if cmgr_ui else ConnManagerUI(ConnManager())

        log.debug('EngineManager inited')

    def run_cmgr_ui(self, inputed_code='', conn_name=''):
        self.cmgr_ui.run()

    def read_conn_list(self) -> None:
        print('Existed connections: {}'.format(
            '"' + '",  "'.join([name for name in self.cmgr_ui.fmgr.read_conf()['conn'].keys()]) + '"'))

    def test_engine(self, engine, type='set'):
        # engine test
        with engine.connect() as conn:
            result = conn.execute(text("select 'Testing engine.'"))
            if result.scalar():
                if type == 'set':
                    log.info('Connect succeed.')
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
                    log.error('Login failed.')
                try_time += 1
                conf_dict = self.cmgr_ui.run('READ', conn_name)
                if conf_dict:
                    if 'pyodbc' in conf_dict['sqlalchemy.url']:
                        # depend your native version
                        conf_dict['sqlalchemy.url'] += '?driver=SQL+Server+Native+Client+11.0'

                    # add kwargs to conf_dict
                    if kwargs:
                        log.info("engine additional kwargs: %s", kwargs)
                        for key, value in kwargs.items():
                            conf_dict['sqlalchemy.' + key] = value
                    log.debug("conf_dict with kwargs: %s", conf_dict)
                    self._engine_dict[conn_name] = engine_from_config(conf_dict, prefix='sqlalchemy.')
                    self.test_engine(self._engine_dict[conn_name])
                failed = True
            except Exception as e:
                log.error("An error occurred. {!r}".format(e.args[-1]))
            finally:
                if try_time > try_max:
                    log.error('Login failed too much time. Stop trying.')

    def get_engine(self, conn_name):
        if self._engine_dict.get(conn_name):
            if self.test_engine(self._engine_dict[conn_name], 'get'):
                return self._engine_dict[conn_name]
            else:
                log.warning(
                    "The engine[{0}] connect failed. Drop it.".format(conn_name))
                self._engine_dict.pop(conn_name)
        else:
            log.warning("The engine[{0}] is not found.".format(conn_name))


if __name__ == '__main__':
    # diff ways to init a instance of EngineManager
    if False:
        # customize from Ignorer and Crypt
        from src.manager.Ignorer import Ignorer  # noqa: E402
        from src.manager.Crypt import Crypt  # noqa: E402
        gitignorer = Ignorer()
        crypter = Crypt(gitignorer=gitignorer)
        cmgr = ConnManager(crypter=crypter, gitignorer=gitignorer)
        cmgr_ui = ConnManagerUI(conn_manager=cmgr)
        manager = EngineManager(cmgr_ui=cmgr_ui)

    if False:
        # customize from ConnManager and ConnManagerUI
        cmgr = ConnManager()
        cmgr_ui = ConnManagerUI(conn_manager=cmgr)
        manager = EngineManager(cmgr_ui=cmgr_ui)

    if True:
        # no custom
        manager = EngineManager()
    manager.read_conn_list()
    manager.set_engine('164', future=True)
    engine_164 = manager.get_engine('164')
    # print(manager._engine_dict)
    # manager.run_cmgr_ui()
