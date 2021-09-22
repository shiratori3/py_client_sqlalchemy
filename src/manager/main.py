#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

# init instance of Manager Class
from src.manager.ConfManager import ConfManager  # noqa: E402
conf = ConfManager()
log.debug('conf inited')

if __name__ == '__main__':
    from src.manager.Ignorer import Ignorer  # noqa: E402
    gitignorer = Ignorer()
    log.debug('gitignorer inited')

    from src.manager.Crypt import Crypt  # noqa: E402
    crypter = Crypt(gitignorer=gitignorer)
    log.debug('crypter inited')

    from src.manager.ConnManager import ConnManager  # noqa: E402
    from src.manager.ConnManager import ConnManagerUI  # noqa: E402
    cmgr = ConnManager(crypter=crypter, gitignorer=gitignorer)
    log.debug('cmgr inited')
    cmgr_ui = ConnManagerUI(conn_manager=cmgr)
    log.debug('cmgr_ui inited')

    from src.manager.EngineManager import EngineManager  # noqa: E402
    emgr = EngineManager(cmgr_ui=cmgr_ui)
    log.info('emgr inited')
