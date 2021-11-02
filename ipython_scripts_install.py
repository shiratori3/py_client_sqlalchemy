#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ipython_scripts_install.py
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
import shutil
from src.manager.BaseFileManager import BaseFileManager


def check_settings(src_path: Path):
    """create and update settings.yaml for 90-start-client.py"""
    ipython_fmgr = BaseFileManager(src_path)

    if 'path_to_add' not in ipython_fmgr.conf_dict.keys():
        print('create path_to_add in settings.yaml under Path[{}]'.format(src_path))
        path_to_add = []
        path_to_add.append(str(cwdPath))
        ipython_fmgr.conf_dict['path_to_add'] = path_to_add
        ipython_fmgr._write_conf()
    else:
        if str(cwdPath) not in ipython_fmgr.conf_dict['path_to_add']:
            print('update path_to_add under Path[{}]'.format(src_path))
            path_to_add = ipython_fmgr.conf_dict['path_to_add']
            path_to_add.append(str(cwdPath))
            ipython_fmgr.conf_dict['path_to_add'] = path_to_add
            ipython_fmgr._write_conf()
            print('add path[{}] to path_to_add under Path[{}]'.format(
                str(cwdPath), src_path))


def files_copy(fname_list: list, src_folder: Path, dst_folder: Path, force_to_cover: bool = False):
    """move the files named name in fname_list under src_folder to dst folder"""

    def file_copy(filename: str, src_folder: Path, dst_folder: Path):
        shutil.copyfile(src_folder.joinpath(filename), dst_folder.joinpath(filename))
        print('{} is moved to {}'.format(
            dst_folder.joinpath(filename), src_folder.joinpath(filename)))

    for filename in fname_list:
        if not src_folder.joinpath(filename).exists():
            file_copy(filename, src_folder, dst_folder)
        elif force_to_cover:
            file_copy(filename, src_folder, dst_folder)


if __name__ == '__main__':
    src_folder = cwdPath.joinpath(r'.ipython\profile_default\startup')
    startup_folder = Path(r'C:\Users\{}\.ipython\profile_default\startup'.format(os.getlogin()))
    if not startup_folder.exists():
        startup_folder.mkdir(parents=True)

    check_settings(src_folder)

    fname_list = ['00-start.py', '90-start-client.py', 'settings.yaml']
    files_copy(fname_list, src_folder, startup_folder, force_to_cover=True)

    print('ipython startup installed.')
