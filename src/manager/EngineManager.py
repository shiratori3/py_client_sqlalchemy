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
from sqlalchemy.engine import Engine
from src.manager.ConnManager import ConnManager  # noqa: E402
from src.manager.ConnManager import ConnManagerUI  # noqa: E402


class EngineManager(object):
    """manage the sqlalchemy.engine which connect to database

    Attrs:
        cmgr_ui: ConnManagerUI(ConnManager), default None
            a instance of ConnManagerUI, if none, create a new one by default
        _engine_dict: dict
            a dict saving the connected engines

    Methods:
        run_cmgr_ui(self, inputed_code='', conn_name='') -> dict or None:
            call the ConnManagerUI.run()
        read_conn_list(self) -> None:
            read the list of conn in conn_info.yaml and print it
        test_engine(self, engine: Engine, type: str = 'set') -> bool:
            test the engine whether connect succeed
        set_engine(self, conn_name: str, try_max: int = 3, **kwargs) -> None:
            read from the conf and connect to database, if success, save to self._engine_dict
        get_engine(self, conn_name: str) -> Engine or None:
            get engine from self._engine_dict
    """
    def __init__(self, cmgr_ui: ConnManagerUI(ConnManager) = None):
        self.cmgr_ui = cmgr_ui if cmgr_ui else ConnManagerUI(ConnManager())
        self._engine_dict = {}

        log.debug('EngineManager inited')

    def run_cmgr_ui(self, inputed_code='', conn_name='') -> dict or None:
        """call the ConnManagerUI.run()"""
        if inputed_code:
            return self.cmgr_ui.run(inputed_code=inputed_code, conn_name=conn_name)
        else:
            return self.cmgr_ui.run()

    def read_conn_list(self) -> None:
        """read the list of conn in conn_info.yaml and print it"""
        print('Existed connections: {}'.format(
            '"' + '",  "'.join([name for name in self.cmgr_ui.fmgr.read_conf()['conn'].keys()]) + '"'))

    def test_engine(self, engine: Engine, type: str = 'set') -> bool:
        """test the engine whether connect succeed"""
        with engine.connect() as conn:
            result = conn.execute(text("select 'Testing engine.'"))
            if result.scalar():
                if type == 'set':
                    log.info('Connect succeed.')
                return True
            else:
                return False

    def set_engine(self, conn_name: str, try_max: int = 3, **kwargs) -> None:
        """read from the conf and connect to database, if success, save to self._engine_dict

        Args:
            conn_name: str
                the name of connection to read from conn_info.yaml
            try_max: int
                the maximum number you can try to connect to a database
        """
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

    def get_engine(self, conn_name: str) -> Engine or None:
        """get engine from self._engine_dict"""
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
