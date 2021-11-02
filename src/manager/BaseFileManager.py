#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   BaseFileManager.py
@Author  :   Billy Zhou
@Time    :   2021/08/22
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

import yaml
import configparser
from src.basic.input_check import input_checking_list  # noqa: E402


class BaseFileManager:
    """manage the operation on the configuration file

    Attrs:
        conf_path: Path, default 'Path(__file__).parents[2].joinpath('conf')'
            Directory of configuration file.
        conf_filename: str, default 'settings.yaml'
            Name of Path of configuration file
        conf_file: Path, Path(self._conf_path).joinpath(self._conf_filename)
            Filepath of configuration file.
        conf_dict: Dict
            Dict readed from conf_file

    Methods:
        read_conf(self) -> None:
            Read configuration from conf_file to conf_dict
        run(self, inputed_code: str, operated_object: str) -> dict or None:
            Operate conf_file according to inputed_code pass by BaseFileManagerUI.

    Staticmethods:
        get_cwdPath(to_str: bool = False) -> Path or str:
            Return Path(BaseFileManager.py).parents[2] as cwdPath
        read_conf_from_file(filepath: Path, encoding: str = '') -> dict or list:
            Read configuration from a file
    """
    def __init__(self, conf_path: Path = cwdPath.joinpath('conf'), conf_filename: str = 'settings.yaml'):
        self._conf_path = Path(conf_path)
        self._conf_filename = conf_filename
        self._conf_file = Path(self._conf_path).joinpath(self._conf_filename)
        self.conf_dict = {}

        # check conf_path and check conf_file
        self._check_conffile()

        # Update according to conf_dict
        self._write_conf()

        log.debug('BaseFileManager inited')

    def _check_path(self, uncheck_path: Path) -> Path:
        """check uncheck_path, if false, replace it with Path(__file__).parents[2]

        Conditions:
            1. uncheck_path == Path('') or str(checked_path) == '.'
            2. Path(checked_path).exists()
        """
        checked_path = uncheck_path
        log.debug("conf_path before checked: %s", checked_path)
        if checked_path == Path('') or str(checked_path) == '.':
            checked_path = cwdPath
            log.debug('Blank inputed path. Using the default path[{0}]'.format(cwdPath))
        if not Path(checked_path).exists():
            Path(checked_path).mkdir(parents=True)
            log.warning("The path[{0}] not existed. Creating.".format(checked_path))
        log.debug("conf_path after checked: %s", checked_path)
        return Path(checked_path)

    def _check_conffile(self) -> None:
        """check _conf_file and the confpath in conf_dict['path']"""
        # check _conf_file exists or not
        if not self._conf_file.exists():
            self._conf_path = self._check_path(self._conf_path)
            self._conf_file = self._conf_path.joinpath(self._conf_filename)
        # read conf_file
        if self._conf_file.exists():
            self.conf_dict = self.read_conf()
        # check the path in conf_dict
        if not self.conf_dict.get('path'):
            log.info('The configuration missing the session[part]')
            log.info('Adding with the blank value')
            self.conf_dict['path'] = {}
        if not self.conf_dict['path'].get('confpath'):
            log.info('The configuration missing the session[part][confpath]')
            log.info('Adding with the default value[{0}]'.format(str(cwdPath)))
            self.conf_dict['path']['confpath'] = str(cwdPath)
        else:
            if self._conf_path == Path('') or str(self._conf_path) == '.':
                self._conf_path = cwdPath
                log.debug('Blank inputed path. Using the default path[{0}]'.format(self._conf_path))
            if Path(self.conf_dict['path']['confpath']) != Path(self._conf_path):
                self.conf_dict['path']['confpath'] = str(Path(self._conf_path))

    def _write_conf(self) -> None:
        with open(str(self._conf_file), 'w') as configfile:
            yaml.dump(self.conf_dict, configfile)

    def read_conf(self) -> dict:
        converted = BaseFileManager.read_conf_from_file(self._conf_file)
        self.conf_dict = converted if converted else {}
        return self.conf_dict

    def run(self, inputed_code: str, operated_object: str) -> dict or None:
        """operation flow according to inputed_code pass by BaseFileManagerUI.

        Rewrite this function by yourself.
        It's better to create a flowchart before writing your code

        Args:
            inputed_code: str
                Supported: 'READ', 'ADD', 'UPDATE', 'DELETE', 'RENAME'
                the relation between inputed_code and object:
                    need existing object: 'READ', 'UPDATE', 'DELETE', 'RENAME'
                    need non-existing object: 'ADD'
            operated_object: str

        Returns:
            return none or a dict when readed.
        """
        if inputed_code == 'READ':
            pass
        elif inputed_code == 'ADD':
            pass
        elif inputed_code == 'UPDATE':
            pass
        elif inputed_code == 'DELETE':
            pass
        elif inputed_code == 'RENAME':
            pass

    @staticmethod
    def get_cwdPath(to_str: bool = False) -> Path or str:
        """return Path(BaseFileManager.py).parents[2] as cwdPath"""
        return cwdPath if not to_str else cwdPath.resolve()

    @staticmethod
    def read_conf_from_file(filepath: Path, encoding: str = '') -> dict or list:
        """Read configuration from file"""
        if Path(filepath).exists() and Path(filepath).is_file():
            if not encoding:
                encoding = None
            if Path(filepath).suffix == '.ini':
                config = configparser.ConfigParser()
                config.read(str(filepath), encoding=encoding)
                data = {s: dict(config.items(s)) for s in config.sections()}
            else:
                with open(str(filepath), encoding=encoding) as configfile:
                    if Path(filepath).suffix == '.yaml':
                        data = yaml.load(configfile, Loader=yaml.Loader)
                    else:
                        data = configfile.readlines()
            return data
        else:
            log.error('Error. Invaild filepath[{}] to read conf.'.format(filepath))
            return {}

    @property
    def conf_path(self):
        return self._conf_path

    @conf_path.setter
    def conf_path(self, new_path: Path or str):
        old_path = self._conf_path
        self._conf_path = self._check_path(new_path)
        if str(old_path) != str(self._conf_path):
            log.info("""The default path of conffile changed.
            From old_path: {0}
            to new_path: {1}""".format(str(old_path), str(self._conf_path)))

            # update self._conf_file and check and update
            self._conf_file = Path(self._conf_path).joinpath(self._conf_filename)
            self._check_conffile()
            self._write_conf()

    @property
    def conf_filename(self):
        return self._conf_filename

    @conf_filename.setter
    def conf_filename(self, new_name: str):
        old_name = self._conf_filename
        self._conf_filename = str(new_name)
        if str(old_name) != str(self._conf_filename):
            log.info("""The filename of conffile changed.
            From old_name: {0}
            to new_name: {1}""".format(str(old_name), str(new_name)))

            # update self._conf_file and check and update
            self._conf_file = Path(self._conf_path).joinpath(self._conf_filename)
            self._check_conffile()
            self._write_conf()


class BaseFileManagerUI:
    """manage the operation between user input code and conf_file

    Attrs:
        fmgr: BaseFileManager
            a BaseFileManager instance.
            fmgr = BaseFileManager(
                conf_path: Path = cwdPath.joinpath('conf'),
                conf_filename: str = 'settings.yaml'
            )
        support_code: List[str], default ['READ', 'UPDATE', 'DELETE', 'RENAME', 'ADD', 'CLEAR']
            a list of supporting code. Inputed code must in this list.
        handling_code: str
            the current of handling inputed code

    Methods:
        run(self, inputed_code: str = '', operated_object: str = '') -> dict or None:
            Alter the operation flow of inputed_code.
            Use the handling_code to record the change of inputed_code.

        _code_read(self, operated_object) -> dict:
            operation of inputed_code 'READ' pass to self.fmgr
        _code_update(self, operated_object) -> None:
            operation of inputed_code 'UPDATE' pass to self.fmgr
        _code_rename(self, operated_object) -> None:
            operation of inputed_code 'RENAME' pass to self.fmgr
        _code_delete(self, operated_object) -> None:
            operation of inputed_code 'DELETE' pass to self.fmgr
        _code_add(self, operated_object) -> None:
            operation of inputed_code 'ADD' pass to self.fmgr
        _code_clear(self) -> None:
            for object in objects_list, call _code_delete(self, object)
    """
    def __init__(self, file_manager: BaseFileManager):
        self._support_code = ['READ', 'UPDATE', 'DELETE', 'RENAME', 'ADD', 'CLEAR']
        self._handling_code = ''  # the code that present the running status
        self.fmgr = file_manager

        log.debug('BaseFileManagerUI inited')

    def _check_handle(self, inputed_code: str) -> None:
        """check inputed code in _upport_code or not, if not, reinput until True."""
        if inputed_code.upper() not in self._support_code:
            log.error('Invaild code[{}] inputed.'.format(inputed_code))
            self._handling_code = input_checking_list(
                self._support_code, 'Please choose your operation.')
        else:
            self._handling_code = inputed_code.upper()

    def run(self, inputed_code: str = '', operated_object: str = '') -> dict or None:
        """operation flow according to inputed_code.

        Rewrite this function by yourself.
        It's better to create a flowchart before writing your code

        Args:
            inputed_code: str
                inputed_code must in _support_code.
                the relation between inputed_code and object:
                    need existing object: 'READ', 'UPDATE', 'DELETE', 'RENAME'
                    need non-existing object: 'ADD'
                    not need object: 'CLEAR'
            operated_object: str
                the object to operated

        Returns:
            return a dict when readed, else None.
        """
        if not inputed_code:
            inputed_code = input_checking_list(
                self._support_code, case_sens=False,
                tip_words='Please choose your operation.'
            )
        # check inputed code in _support_code or not, if not, reinput until True.
        self._check_handle(inputed_code)

        # here is a simple flow, without additional input and redirect
        if self._handling_code == 'READ':
            self._code_read(operated_object)
        elif self._handling_code == 'UPDATE':
            self._code_update(operated_object)
        elif self._handling_code == 'DELETE':
            self._code_delete(operated_object)
        elif self._handling_code == 'RENAME':
            self._code_rename(operated_object)
        elif self._handling_code == 'ADD':
            self._code_add(operated_object)
        elif self._handling_code == 'CLEAR':
            self._code_clear()
        log.info('ManagaerUI run over.')

    def _code_read(self, operated_object) -> dict:
        """rewrite this function by your need"""
        log.info('Object[{}] readed.'.format(operated_object))
        return self.fmgr.run('READ', operated_object)

    def _code_update(self, operated_object) -> None:
        """rewrite this function by your need"""
        self.fmgr.run('UPDATE', operated_object)
        log.info('Object[{}] updated.'.format(operated_object))

    def _code_rename(self, operated_object) -> None:
        """rewrite this function by your need"""
        self.fmgr.run('RENAME', operated_object)
        log.info('Object[{}] renamed.'.format(operated_object))

    def _code_delete(self, operated_object) -> None:
        """rewrite this function by your need"""
        self.fmgr.run('DELETE', operated_object)
        log.info('Object[{}] deleted.'.format(operated_object))

    def _code_add(self, operated_object) -> None:
        """rewrite this function by your need"""
        self.fmgr.run('ADD', operated_object)
        log.info('Object[{}] added.'.format(operated_object))

    def _code_clear(self) -> None:
        """rewrite this function by your need"""
        # self._objects_list should be readed in self.__init__()
        self._objects_list = []
        for i in self._objects_list:
            self.fmgr.run('DELETE', i)
        log.info('Objects_list cleared.')

    @property
    def handling_code(self):
        return self._handling_code

    @handling_code.setter
    def handling_code(self, new_code: str):
        self._check_handle(new_code)
        self._handling_code = new_code


if __name__ == '__main__':
    file_manager = BaseFileManager()
    manager = BaseFileManagerUI(file_manager)
    log.info('file_manager.get_cwdPath(): %s', file_manager.get_cwdPath())
    log.info('manager.run(): %s', manager.run())
