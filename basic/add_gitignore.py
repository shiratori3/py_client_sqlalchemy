#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   add_gitignore.py
@Author  :   Billy Zhou
@Time    :   2021/06/14
@Version :   0.0.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from conf_manage import readConf  # noqa: E402
cwdPath = Path(readConf()["path"]['cwd'])


def add_gitignore(ignore_path, under_gitignore=False):
    ignore_list = [ignore_path]
    if under_gitignore:
        ignore_list.append('/gitignore/')
    # git上传忽略对应文件
    with open(cwdPath.joinpath('.gitignore'), 'a+', encoding='utf-8') as f:
        status_ignored = False

        f.seek(0, 0)  # back to the start
        for i in f.readlines():
            logging.debug(i.replace('\n', ''))
            if i.replace('\n', '') in ignore_list:
                status_ignored = True
                break
        if not status_ignored:
            f.write('\n' + ignore_path + '\n')
            print(ignore_path + ' added to .gitignore')
        print('status_ignored: %s' % status_ignored)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    add_gitignore('/rsa', under_gitignore=False)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
