#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ipython_scripts.py
@Author  :   Billy Zhou
@Time    :   2021/11/02
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]  # the num depend on your filepath
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr
log = logmgr.get_logger(__name__)

import shutil
from src.manager.BaseFileManager import BaseFileManager


def check_ipython_settings(src_path: Path) -> dict:
    """create and update settings.yaml for 90-start-client.py, and return the dict of settings"""
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

    return ipython_fmgr.conf_dict


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
            print('Path[{}] already exists. Force to cover'.format(src_folder.joinpath(filename)))
            file_copy(filename, src_folder, dst_folder)
        else:
            print('Path[{}] already exists. Pass.'.format(src_folder.joinpath(filename)))


if __name__ == '__main__':
    import os

    # install ipython scripts
    src_folder = cwdPath.joinpath(r'res\dev\.ipython\profile_default\startup')
    startup_folder = Path(r'C:\Users\{}\.ipython\profile_default\startup'.format(os.getlogin()))
    if not startup_folder.exists():
        startup_folder.mkdir(parents=True)

    if True:
        settings = check_ipython_settings(src_folder)
        print(f"settings: \n{settings}")

    if True:
        fname_list = ['00-start.py', '90-start-client.py', 'settings.yaml']
        files_copy(fname_list, src_folder, startup_folder, force_to_cover=False)
