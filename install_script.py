#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   install_script.py
@Author  :   Billy Zhou
@Time    :   2021/11/02
@Desc    :   None
'''

import sys
from pathlib import Path
cwdPath = Path(__file__).parents[0]  # the num depend on your filepath
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr
log = logmgr.get_logger(__name__)

import os
from src.setup.ipython_scripts import check_ipython_settings
from src.setup.ipython_scripts import files_copy
from src.setup.conda_check import find_conda_path
from src.setup.conda_check import add_conda_path
from src.setup.conda_check import check_conda_bat
from src.setup.conda_check import check_conda_settings
from src.setup.conda_check import create_conda_env


if __name__ == '__main__':
    # init
    usr_folder = Path(os.path.expanduser('~'))
    scripts_folder = cwdPath.joinpath(r'res\dev\.ipython\profile_default\startup')
    startup_folder = usr_folder.joinpath(r'.ipython\profile_default\startup')
    if not startup_folder.exists():
        startup_folder.mkdir(parents=True)

    # find the basepath of conda
    conda_basepath = find_conda_path(folder_keyword='conda')

    # install conda env
    if True:
        # check and add conda_basepath to sys path
        add_conda_path(conda_basepath)

        # check conda.bat and update conda environment variables
        check_conda_bat(conda_basepath, add_path=True)

        # check and update settings in .condarc file
        check_conda_settings(usr_folder, force_to_cover=True)

        # check and create conda env named py_sql_client
        create_conda_env('py_sql_client', cwdPath.joinpath('requirements_conda_py_sql_client_win.yaml'), force_to_install=False)

        # check and add py_sql_client to sys path
        add_conda_path(conda_basepath.joinpath('envs\\py_sql_client'))

    # install ipython scripts
    if True:
        check_ipython_settings(scripts_folder)

        fname_list = ['00-start.py', '90-start-client.py', 'settings.yaml']
        files_copy(fname_list, scripts_folder, startup_folder, force_to_cover=True)
