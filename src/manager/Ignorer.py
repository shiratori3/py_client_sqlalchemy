#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   add_gitignore.py
@Author  :   Billy Zhou
@Time    :   2021/06/15
@Version :   1.1.0
@Desc    :   None
'''


import sys
import logging
log = logging.getLogger(__name__)

from pathlib import Path  # noqa: E402
sys.path.append(str(Path(__file__).parents[2]))

from src.manager.ConfManager import cwdPath  # noqa: E402


class Ignorer:
    def __init__(self, savepath: Path = cwdPath) -> None:
        self.savepath = savepath
        self.ignorefile = savepath.joinpath('.gitignore')

        # create if not exist
        if not self.ignorefile.exists():
            log.info('No existing gitignore file. Creating a new one.')
            ignore_init = [
                '/.vscode/', '*__pycache__/', '*.ipynb_checkpoints/', '*.ipynb', '/conf/', '*.yaml', '/log/', '*.log', '/res/pro/', '/bin/*.py', '!template.*', '!logging.yaml'
            ]
            with open(self.ignorefile, 'a+', encoding='utf-8') as f:
                for ignore in ignore_init:
                    f.write(ignore + '\n')
            log.info('Finished.')

        # read from gitignore file
        self.ignorelist = self.read_gitignore()

    def read_gitignore(self):
        self.ignorelist = []
        with open(self.ignorefile, encoding='utf-8') as f:
            line = f.readline()
            while line:
                self.ignorelist.append(line[:-1])
                line = f.readline()
        log.debug("ignorelist: {}".format(self.ignorelist))
        return self.ignorelist

    def add_gitignore(self, ignore_path: Path or str):
        """don't update ignore_path while update to git"""
        with open(self.ignorefile, 'a+', encoding='utf-8') as f:
            ignored = False

            f.seek(0, 0)  # back to the start
            for i in f.readlines():
                log.debug(i[:-1])  # the last char \n
                if str(ignore_path) == i[:-1]:
                    ignored = True
                    break
            log.debug('ignored: {}'.format(ignored))
            if not ignored:
                if i[-1] != '\n':
                    f.write('\n')
                f.write(str(ignore_path) + '\n')
                log.info('{} added to .gitignore'.format(ignore_path))


gitignorer = Ignorer()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    gitignorer.read_gitignore()
    gitignorer.add_gitignore('/rsa/')
    log.info(gitignorer.savepath.parts)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
