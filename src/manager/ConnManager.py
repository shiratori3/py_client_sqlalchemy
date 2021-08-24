#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ConnManager.py
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

import json
from urllib.parse import quote as urlquote
from src.basic.input_check import input_default  # noqa: E402
from src.basic.input_check import input_pwd  # noqa: E402
from src.basic.input_check import input_checking_list  # noqa: E402
from src.basic.input_check import input_checking_YN  # noqa: E402
from src.basic.compare import dict_compare  # noqa: E402
from src.manager.Ignorer import Ignorer  # noqa: E402
from src.manager.Crypt import Crypt  # noqa: E402
from src.manager.BaseFileManager import BaseFileManager  # noqa: E402
from src.manager.BaseFileManager import BaseFileManagerUI  # noqa: E402


class ConnManager(BaseFileManager):
    """manage the operation between conn_info_file and conn_txt_file

    Attrs:
        conf_path: Path, default cwdPath.joinpath('conf\\conn')
            Directory of configuration file.
        file_encrypt: bool, default True,
            whether to encrypt conn_info when save
        crypter: Crypt, default None
            a Crypt instance to encrypt and decrypt
        gitignorer: Ignorer, default None
            a Ignorer instance to add '/conf/rsa/' or the conf_path to .gitignore

        _support_dialect: List[str]
        _support_driver: Dict[List[str]]
            the dialect and driver supported. You can add more if it is in the sqlalchemy engine
        conf_file: Path
            Filepath of configuration file
        conf_dict: Dict[str]
            Dict readed from conf_file, format: {'conn_name': conn_filepath}
        _conn_conf: Dict[str]
            a dict of connection configuration info for sqlalchemy engine

    Methods:
        run(self, inputed_code: str, conn_name: str) -> dict or None:
            operation flow according to inputed_code pass by BaseFileManagerUI.
    """
    def __init__(
            self,
            conf_path: Path = cwdPath.joinpath('conf\\conn'), file_encrypt: bool = True,
            crypter: Crypt = None, gitignorer: Ignorer = None):
        super().__init__(conf_path=conf_path, conf_filename='conn_info.yaml')

        self._file_encrypt = file_encrypt
        self._support_dialect = ['mysql', 'mssql', 'sqlite']
        self._support_driver = {
            'mysql': ['pymysql', 'mysqldb', 'no driver'],
            'mssql': ['pyodbc', 'pymssql'],
            'sqlite': ['no driver'],
        }
        self._conn_conf = {}

        # check ignore
        if gitignorer:
            self._gitignorer = gitignorer
        else:
            if crypter:
                # use the instance of Ignorer in crypter
                if hasattr(crypter, '_gitignorer'):
                    log.info('Read gitignorer from crypter')
                    self._gitignorer = crypter._gitignorer
            else:
                # init gitignorer
                log.info('initing Ignorer')
                self._gitignorer = Ignorer()
        if Path(conf_path) == cwdPath.joinpath('conf\\rsa'):
            self._gitignorer.add_gitignore('/conf/rsa/')
        else:
            self._gitignorer.add_gitignore(str(conf_path))

        # decide whether to encrypt file
        if self._file_encrypt:
            if crypter:
                self.__crypter = crypter
            else:
                log.info('initing Crypt')
                self.__crypter = Crypt(gitignorer=gitignorer)

        # check conn_dict while init
        self._check_conf_dict()

        log.debug('ConnManager inited')

    def _check_conf_dict(self) -> None:
        """check the conf_dict to keep the conn_file in path and filepath in dict correct"""
        self.conf_dict = self.read_conf()
        conn_names = [f.name.replace('.txt', '') for f in list(self._conf_path.glob('*.txt'))]

        if self.conf_dict.get('conn'):
            # check conn and conn_file
            # check redundancy conn_file not in conf_dict['conn']
            for conn_name in conn_names:
                if not self.conf_dict['conn'].get(conn_name):
                    log.warning('The file of connection[%s] not in conn_dict.' % conn_name)
                    log.warning('Remove the redundancy file.')
                    Path(self._conf_path.joinpath(conn_name + ".txt")).unlink()

            # check conn in conf_dict['conn'] have right filepath or not
            error_conn_name = []
            for conn_name, fpath in self.conf_dict['conn'].items():
                # conn_name with file
                if conn_name in conn_names:
                    if not Path(fpath).exists():
                        log.warning(
                            'The file of connection[%s] in conn_dict is wrong.' % conn_name)
                        log.warning('Fix the filepath.')
                        self.conf_dict['conn'][conn_name] = str(self._conf_path.joinpath(conn_name + ".txt"))
                # conn_name with no file
                else:
                    log.warning('The file of connection[%s] not exists.' % conn_name)
                    log.warning('Remove the redundancy connection.')
                    error_conn_name.append(conn_name)
            for conn_name in error_conn_name:
                self.conf_dict['conn'].pop(conn_name)
        else:
            # init
            self.conf_dict['conn'] = {}

        # update conf_dict
        self._write_conf()

    def run(self, inputed_code: str, conn_name: str) -> dict or None:
        """operation flow according to inputed_code pass by BaseFileManagerUI.

        Args:
            inputed_code: str
                inputed_code should in ['READ', 'ADD', 'UPDATE', 'DELETE', 'RENAME'].

                the relation between inputed_code and object:
                    need existing object: 'READ', 'UPDATE', 'DELETE', 'RENAME'
                    need non-existing object: 'ADD'
            conn_name: str

        Returns:
            return a dict when readed, else None.
        """
        self.conf_dict = self.read_conf()
        if inputed_code == 'READ':
            # read the _conn_conf from conn_file
            return self._read_conn_conf(conn_name)
        elif inputed_code == 'ADD':
            # write the _conn_conf to conn_file and update self.conf_dict
            self._conn_conf = {
                'sqlalchemy.url': self._create_conn_url(),
            }
            self._write_conn_conf(conn_name)
            self.conf_dict['conn'][conn_name] = str(self._conf_path.joinpath(conn_name + ".txt"))
        elif inputed_code == 'UPDATE':
            # read the _conn_conf from conn_file and compare with inputed _conn_conf
            old_conf = self._read_conn_conf(conn_name)
            new_conf = {
                'sqlalchemy.url': self._create_conn_url(),
            }
            self._conn_conf = dict_compare(
                old_conf, new_conf, diff_autoadd=True)
            self._write_conn_conf(conn_name)
        elif inputed_code == 'DELETE':
            Path(self.conf_dict['conn'][conn_name]).unlink()
            self.conf_dict['conn'].pop(conn_name)
        elif inputed_code == 'RENAME':
            # input new name
            tip_words = 'Please input the NEW name for connection[{0}].'.format(conn_name)
            conn_renamed = input_default('localhost', tip_words)
            while set([conn_renamed]) & set([name for name, path in self.conf_dict['conn'].items()]):
                print('The NEW name[%s] already USED. Please input a NEW ONE.' % conn_renamed)
                conn_renamed = input_default('localhost', tip_words)
            # rename the txt file of conn_name
            conn_name_filepath = Path(self.conf_dict['conn'][conn_name]).parents[0]
            conn_renamed_filepath = Path(conn_name_filepath).joinpath(conn_renamed + '.txt')
            Path(self.conf_dict['conn'][conn_name]).rename(conn_renamed_filepath)
            # update dict
            self.conf_dict['conn'].pop(conn_name)
            self.conf_dict['conn'][conn_renamed] = str(conn_renamed_filepath)
            log.info('Connection[{0}] renamed to {1}.'.format(conn_name, conn_renamed))

        self._write_conf()
        print('FileManager run over.')

    def _write_conn_conf(self, conn_name) -> None:
        """write the _conn_conf to self._conf_path.joinpath(conn_name + '.txt')"""
        with open(self._conf_path.joinpath(conn_name + '.txt'), 'w') as file_obj:
            if self._file_encrypt:
                file_obj.write(self.__crypter.encrypt(json.dumps(self._conn_conf)))
            else:
                json.dump(self._conn_conf, file_obj)

    def _read_conn_conf(self, conn_name) -> dict:
        """read the _conn_conf from self.conf_dict['conn'][conn_name]"""
        with open(self.conf_dict['conn'][conn_name]) as file_obj:
            data = file_obj.read() if not self._file_encrypt else self.__crypter.decrypt(file_obj.read())
        log.debug('data: %s', data)
        self._conn_conf = json.loads(data)
        return self._conn_conf

    def _create_conn_url(self) -> dict:
        """create a conf_url to connect to sqlalchemy engine"""
        dialect = input_checking_list(
            self._support_dialect, 'Please choose the database dialect.', case_sens=True)
        driver = input_checking_list(
            self._support_driver[dialect], 'Please choose the driver.', case_sens=True)
        driver = '' if driver == 'no driver' else driver
        dialect_driver = dialect + '+' + driver if driver else dialect
        if dialect != 'sqlite':
            username = input_default('sa', 'Please input username: ')
            password = urlquote(input_pwd().strip())
            host = input_default('localhost:8080', 'Please input host[:port]: ')
            database = input_default('master', 'Please input database: ')

            conf_url = dialect_driver + '://' + username + ':' + password + '@' + host + '/' + database
        else:
            path = input_default(':memory:', """
            Using sqlite3 database.
            To use :memory:, input :memory:
            Input relative path, such as /foo.db
            Input absolute path in Windows, such as /C:\\path\\to\\foo.db
            Input absolute path in Unix/Mac, such as //absolute/path/to/foo.db
            Please input path: """.replace('            ', ''))

            path = '' if path == ':memory:' else path
            conf_url = dialect_driver + '://' + path

        return conf_url


class ConnManagerUI(BaseFileManagerUI):
    """manage the operation between user input code and ConnManager

    Attrs:
        support_code: List[str], default ['READ', 'UPDATE', 'DELETE', 'RENAME', 'ADD', 'CLEAR']
            a list of supporting code. Inputed code must in this list.
        handling_code: str
            the current of handling inputed code
        conn_manager: ConnManager, default None
            A instance of ConnManager

        _conn_list: list
            the list of connections saved in conf_file
        _selected_conn: str
            the connection to operate
        _default_name: str
            the default name of new connection
    """
    def __init__(self, conn_manager: ConnManager = None):
        conn_manager = conn_manager if conn_manager else ConnManager()
        super().__init__(conn_manager)

        self._conn_list = []
        self._selected_conn = ''
        self._default_name = 'NewConnection'

        log.debug('ConnManagerUI inited')

    def _check_included(self, conn_name: str = '') -> None:
        """read conf file of connections and check whether conn_name in conn_list"""
        self.conf_dict = self.fmgr.read_conf()
        self._selected_conn = ''
        if self.conf_dict.get('conn'):
            self._conn_list = [name for name in self.conf_dict['conn'].keys()]
            conn_list_str = '"' + '",  "'.join(self._conn_list) + '"'
            log.debug('Existed connections: {}'.format(conn_list_str))
            # check whether conn_name in conn_list
            if conn_name:
                if conn_name in self._conn_list:
                    log.info('Connection[%s] in conn_list.' % conn_name)
                    self._selected_conn = conn_name
                else:
                    log.info('Connection[%s] not in conn_list.' % conn_name)
        else:
            print('No existing connections.')

    def run(self, inputed_code: str = '', conn_name: str = '') -> dict or None:
        """operate according to inputed_code.

        Operation flow of each inputed_code like this:
            Read  → Existed     → Readed
                  → Not Existed → Read existed or not → Readed
                                                      → To add or not
            Update works like Read

            Add   → Not Existed → Added
                  → Existed     → Update or not
            Del   → Existed     → Deleted
                  → Not Existed → Delete existed or not
            Rename works like Del

            Clear → Existed     → Cleared
                  → Not Existed → To add or not

        Args:
            inputed_code: str
                inputed_code must in _support_code.

                the relation between inputed_code and object:
                    need existing object: 'READ', 'UPDATE', 'DELETE', 'RENAME'
                    need non-existing object: 'ADD'
                    not need object: 'CLEAR'
            operated_object: str

        Returns:
            return a dict when readed, else None.
        """
        if not inputed_code:
            inputed_code = input_checking_list(
                self._support_code, case_sens=False,
                tip_words='Please choose your operation.'
            )
        # check inputed code in _upport_code or not, if not, reinput until True.
        self._check_handle(inputed_code)
        # read conf file of connections and check whether conn_name in conn_list
        self._check_included(conn_name)

        # handle the conf_file and txt file of connections according to inputed_code
        # not existing connection in conf_file
        if not self._conn_list:
            # not need object: 'CLEAR'
            if self._handling_code == 'CLEAR':
                print('No existing connections to clear.')
            else:
                # need non-existing object: 'ADD'
                if self._handling_code != 'ADD':
                    YN = input_checking_YN(
                        'No existing connection. Unvaild operation. To add a new connection?')
                    if YN != 'Y':
                        print('Canceled.')
                    else:
                        self._code_add(conn_name)
                else:
                    self._code_add(conn_name)
        else:
            # not need object: 'CLEAR'
            if self._handling_code == 'CLEAR':
                self._code_clear()
            else:
                # need non-existing object: 'ADD'
                if self._handling_code == 'ADD':
                    # self._selected_conn meanings that self._check_conn_included() return True
                    if self._selected_conn:
                        YN = input_checking_YN(
                            'Connection[{0}] already existed. Update it?'.format(self._selected_conn))
                        if YN == 'Y':
                            self._code_update(self._selected_conn)
                        else:
                            print('Canceled.')
                    else:
                        # conn_name maybe blank
                        self._code_add(conn_name)
                # need existing object: 'READ', 'UPDATE', 'DELETE', 'RENAME'
                else:
                    # not self._selected_conn meanings that self._check_conn_included() return False
                    if not self._selected_conn:
                        YN = input_checking_YN(
                            'Connection[{0}] not existed to {1}. Choose existing one?'.format(
                                conn_name, self._handling_code))
                        if YN != 'Y':
                            print('Canceled.')
                            if self._handling_code in ['READ', 'UPDATE'] and conn_name:
                                YN = input_checking_YN(
                                    'Add the Connection[{0}]?'.format(conn_name))
                                if YN != 'Y':
                                    print('Canceled.')
                                else:
                                    self._code_add(conn_name)
                        else:
                            self._selected_conn = input_checking_list(
                                self._conn_list, case_sens=True,
                                tip_words='Please choose the connection to {0}.'.format(
                                    self._handling_code))

                    if self._selected_conn:
                        if self._handling_code == 'READ':
                            return self._code_read(self._selected_conn)
                        elif self._handling_code == 'UPDATE':
                            self._code_update(self._selected_conn)
                        elif self._handling_code == 'DELETE':
                            self._code_delete(self._selected_conn)
                        elif self._handling_code == 'RENAME':
                            self._code_rename(self._selected_conn)
        print('ConnUI run over.')

    def _code_read(self, conn_name) -> dict:
        conn_conf = self.fmgr.run('READ', conn_name)
        log.info('Connection[%s] readed.' % conn_name)
        return conn_conf

    def _code_update(self, conn_name) -> None:
        self.fmgr.run('UPDATE', conn_name)
        log.info('Connection[%s] updated.' % conn_name)

    def _code_rename(self, conn_name) -> None:
        self.fmgr.run('RENAME', conn_name)
        log.info('Connection[%s] renamed.' % conn_name)

    def _code_delete(self, conn_name) -> None:
        self.fmgr.run('DELETE', conn_name)
        log.info('Connection[%s] deleted.' % conn_name)

    def _code_add(self, conn_name='') -> None:
        # check whether conn_name is vaild and conn_name in conn_list
        # self._selected_conn meanings that _check_included(conn_name) return True
        if not conn_name or self._selected_conn:
            tips_word = 'Please input the NEW connection name to ADD.'
            conn_name = input_default(self._default_name, tips_word)
            self._check_included(conn_name)
            while self._selected_conn:
                conn_name = input_default(self._default_name, tips_word)
                self._check_included(conn_name)
        self.fmgr.run('ADD', conn_name)
        log.info('Connection[%s] added.' % conn_name)

    def _code_clear(self) -> None:
        YN = input_checking_YN(
            tip_words='Attension! This will delete all existing connections. Are you sure?',
            default_Y=False)
        if YN == 'Y':
            for conn in self._conn_list:
                self._code_delete(conn)
            print('Connections cleared.')
        else:
            print('Canceled.')

    @property
    def default_name(self):
        return self._default_name

    @default_name.setter
    def default_name(self, new_name: str):
        old_name = self._default_name
        self._default_name = str(new_name)
        log.info("""The default name of new connections changed.
        From {0}
        to {1}""".format(old_name, str(new_name)))


if __name__ == '__main__':
    gitignorer = Ignorer()
    crypter = Crypt(gitignorer=gitignorer)

    cmgr = ConnManager(crypter=crypter, gitignorer=gitignorer)
    cmgr_ui = ConnManagerUI(conn_manager=cmgr)
    print(cmgr._conf_path)
    # print(cmgr_ui.run())
