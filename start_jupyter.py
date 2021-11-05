#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   start_jupyter.py
@Author  :   Billy Zhou
@Time    :   2021/08/24
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[0]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

import shlex
from subprocess import Popen


if __name__ == '__main__':
    notebook_dir = cwdPath.joinpath('bin')

    # start jupyter notebook in notebook_dir
    try:
        # NotebookApp.notebook_dir has been removed to ServerApp.root_dir
        # NBClassic runs the Jupyter Notebook frontend on the Jupyter Server backend
        command = 'conda.bat activate py_sql_client && jupyter nbclassic --ServerApp.root_dir={}'.format(notebook_dir).replace('\\', '/')
        log.debug("command: {}".format(command))
        log.debug("command splited: {}".format(shlex.split(command)))
        proc = Popen(shlex.split(command))
        print("Start notebook from Nbclassic succeed")
    except IOError as e:
        log.error("An error occurred. {}".format(e.args))
        log.error("Start notebook from Nbclassic failed")

        command = 'conda.bat activate py_sql_client && jupyter notebook --notebook-dir={}'.format(notebook_dir).replace('\\', '/')
        log.debug("command: {}".format(command))
        log.debug("command splited: {}".format(shlex.split(command)))
        proc = Popen(shlex.split(command))
