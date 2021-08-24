#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Ignorer.py
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


class Ignorer:
    """manage the ignored paths and files in .gitignore

    Attrs:
        savepath: Path, default cwdPath
            the directory to save the .gitignore file
        ignorefile
            the filepath of .gitignore
        ignorelist
            a list of items in .gitignore
        """
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

        log.debug('Ignorer inited')

    def read_gitignore(self) -> list:
        """read the .gitignore file"""
        self.ignorelist = []
        with open(self.ignorefile, encoding='utf-8') as f:
            line = f.readline()
            while line:
                self.ignorelist.append(line[:-1])
                line = f.readline()
        log.debug("ignorelist: {}".format(self.ignorelist))
        return self.ignorelist

    def add_gitignore(self, ignore_path: Path or str) -> None:
        """add path or file to .gitignore file"""
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


if __name__ == '__main__':
    gitignorer = Ignorer()
    gitignorer.read_gitignore()
    gitignorer.add_gitignore('/rsa/')
    log.info("gitignorer.savepath.parts: {}".format(gitignorer.savepath.parts))
