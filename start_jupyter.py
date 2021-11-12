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
from src.setup.conda_check import find_conda_path
from src.setup.conda_check import check_conda_bat
from src.setup.conda_check import check_conda_env


if __name__ == '__main__':
    notebook_dir = cwdPath.joinpath('bin')

    # find the basepath of conda
    conda_basepath = find_conda_path(folder_keyword='conda')

    # check conda.bat and update conda environment variables
    check_conda_bat(conda_basepath, add_path=True)

    # generate command
    cmd_env = ''
    command = 'jupyter nbclassic --ServerApp.root_dir={}'.format(notebook_dir).replace('\\', '/')
    if check_conda_env('py_sql_client'):
        print('conda env[py_sql_client] exists. Try to start jupyter notebook from conda env[py_sql_client]')
        cmd_env = 'conda.bat activate py_sql_client && '
        command = cmd_env + command
    else:
        print('conda env[py_sql_client] not exists. Try to start jupyter notebook from current env.')

    # start jupyter notebook in notebook_dir
    try:
        # NotebookApp.notebook_dir has been removed to ServerApp.root_dir
        # NBClassic runs the Jupyter Notebook frontend on the Jupyter Server backend
        log.info("command splited: {}".format(shlex.split(command)))
        proc = Popen(shlex.split(command))
        print("Start notebook from Nbclassic succeed")
    except IOError as e:
        log.error("An error occurred. {}".format(e.args))
        log.error("Start notebook from Nbclassic failed")

        command = cmd_env + 'jupyter notebook --notebook-dir={}'.format(notebook_dir).replace('\\', '/')
        log.debug("command splited: {}".format(shlex.split(command)))
        proc = Popen(shlex.split(command))
