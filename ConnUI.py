#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ConnUI.py
@Author  :   Billy Zhou
@Time    :   2021/07/30
@Version :   1.0.0
@Desc    :   None
'''

import logging
import json
# import yaml
from pathlib import Path
from urllib.parse import quote as urlquote

from basic.add_gitignore import add_gitignore
from basic.input_check import input_default
from basic.input_check import input_pwd
from basic.input_check import input_checking_list
from basic.input_check import input_checking_YN
from basic.RSA_encrypt import CheckRSAKeys
from basic.RSA_encrypt import Encrypt
from basic.RSA_encrypt import Decrypt
from conf_manage import readConf
from conf_manage import dict_compare
cwdPath = Path(readConf()["path"]['cwd'])


class ConnUI(object):
    # manage the operation between user input and conn_info_file
    def __init__(
            self, conn_path=cwdPath.joinpath('gitignore\\conn'),
            file_encrypt=True, pubkeyfile=None, prikeyfile=None):
        self._support_code = ['READ', 'UPDATE', 'DELETE', 'RENAME', 'ADD', 'CLEAR']
        # need existing object: 'READ', 'UPDATE', 'DELETE', 'RENAME'
        # need non-existing object: 'ADD'
        # not need object: 'CLEAR'
        self._handling_code = ''
        self._conn_list = []
        self._selected_conn = ''
        self._default_name = 'NewConnection'
        self.fmgr = FileManager(conn_path, file_encrypt, pubkeyfile, prikeyfile)

    def _check_handle(self, inputed_code):
        # check inputed code in _upport_code or not, if not, reinput until True.
        if inputed_code.upper() not in self._support_code:
            logging.error('Invaild code inputed.')
            self._handling_code = input_checking_list(
                self._support_code, 'Please choose your operation.')
        else:
            self._handling_code = inputed_code.upper()

    def _check_conn_included(self, conn_name):
        # read conf file of connections and check whether conn_name in conn_list
        self.conf_dict = self.fmgr.read_conf()
        self._selected_conn = ''
        if self.conf_dict:
            self._conn_list = [name for name, path in self.conf_dict.items()]
            conn_list_str = '"' + '",  "'.join(self._conn_list) + '"'
            logging.info('Existed connections: %s', conn_list_str)
            # check whether conn_name in conn_list
            if conn_name:
                if conn_name in self._conn_list:
                    logging.info('Connection[%s] in conn_list.' % conn_name)
                    self._selected_conn = conn_name
                else:
                    logging.info('Connection[%s] not in conn_list.' % conn_name)
        else:
            logging.info('No existing connections.')

    def run(self, inputed_code='', conn_name=''):
        if not inputed_code:
            inputed_code = input_checking_list(
                self._support_code, case_sens=False,
                tip_words='Please choose your operation.'
            )
        # check inputed code in _upport_code or not, if not, reinput until True.
        self._check_handle(inputed_code)
        # read conf file of connections and check whether conn_name in conn_list
        self._check_conn_included(conn_name)

        # handle the conf_file and txt file of connections according to inputed_code
        # not existing connection in conf_file
        if not self._conn_list:
            # not need object: 'CLEAR'
            if self._handling_code == 'CLEAR':
                logging.info('No existing connections to clear.')
            else:
                # need non-existing object: 'ADD'
                if self._handling_code != 'ADD':
                    YN = input_checking_YN(
                        'No existing connection. Unvaild operation. To add a new connection?')
                    if YN != 'Y':
                        logging.info('Canceled.')
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
                            logging.info('Canceled.')
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
                            logging.info('Canceled.')
                            if self._handling_code in ['READ', 'UPDATE'] and conn_name:
                                YN = input_checking_YN(
                                    'Add the Connection[{0}]?'.format(conn_name))
                                if YN != 'Y':
                                    logging.info('Canceled.')
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
        logging.info('ConnUI run over.')

    def _code_read(self, conn_name):
        conn_conf = self.fmgr.run('READ', conn_name)
        logging.info('Connection[%s] readed.' % conn_name)
        return conn_conf

    def _code_update(self, conn_name):
        self.fmgr.run('UPDATE', conn_name)
        logging.info('Connection[%s] updated.' % conn_name)

    def _code_rename(self, conn_name):
        self.fmgr.run('RENAME', conn_name)
        logging.info('Connection[%s] renamed.' % conn_name)

    def _code_delete(self, conn_name):
        self.fmgr.run('DELETE', conn_name)
        logging.info('Connection[%s] deleted.' % conn_name)

    def _code_add(self, conn_name=''):
        # check whether conn_name is vaild and conn_name in conn_list
        # self._selected_conn meanings that _check_conn_included(conn_name) return True
        if not conn_name or self._selected_conn:
            tips_word = 'Please input the NEW connection name to ADD.'
            conn_name = input_default(self._default_name, tips_word)
            self._check_conn_included(conn_name)
            while self._selected_conn:
                conn_name = input_default(self._default_name, tips_word)
                self._check_conn_included(conn_name)
        self.fmgr.run('ADD', conn_name)
        logging.info('Connection[%s] added.' % conn_name)

    def _code_clear(self):
        YN = input_checking_YN(
            tip_words='Attension! This will delete all existing connections. Are you sure?',
            default_Y=False)
        if YN == 'Y':
            for conn in self._conn_list:
                self._code_delete(conn)
            logging.info('Connections cleared.')
        else:
            logging.info('Canceled.')

    @property
    def default_name(self):
        return self._default_name

    @default_name.setter
    def default_name(self, new_name):
        old_name = self._default_name
        self._default_name = str(new_name)
        logging.info("""The default name of new connections changed.
        From {0}
        to {1}""".format(old_name, str(new_name)))

    @property
    def handling_code(self):
        return self._handling_code

    @handling_code.setter
    def handling_code(self, new_code):
        self._check_handle(new_code)
        self._handling_code = new_code


class FileManager(object):
    # manage the operation between conn_info_file and conn_txt_file
    def __init__(self, conn_path, file_encrypt, pubkeyfile, prikeyfile):
        self._file_encrypt = file_encrypt
        self.__pubkeyfile = pubkeyfile
        self.__prikeyfile = prikeyfile
        self._conn_path = Path(conn_path)
        self._conf_filename = 'conn_info.json'
        self._conn_conf = {}
        self._support_dialect = ['mysql', 'mssql', 'sqlite']
        self._support_driver = {
            'mysql': ['pymysql', 'mysqldb', 'no driver'],
            'mssql': ['pyodbc', 'pymssql'],
            'sqlite': ['no driver'],
        }
        self.conf_dict = {}

        if self._file_encrypt:
            if pubkeyfile and pubkeyfile:
                self.__pubkeyfile, self.__prikeyfile = pubkeyfile, prikeyfile
            else:
                self.__pubkeyfile, self.__prikeyfile = CheckRSAKeys()
        else:
            self.__pubkeyfile, self.__prikeyfile = None, None

        # check conn_path and conn_dict while init
        self._conn_path = self._check_path(self._conn_path)
        self._check_conn_dict()

        # check ignore
        add_gitignore('/gitignore/conn/', under_gitignore=True)

    def _check_path(self, uncheck_path) -> None:
        # check Path.is_dir() and exists()
        checked_path = uncheck_path
        if not Path(checked_path).is_dir():
            checked_path = cwdPath.joinpath('gitignore\\conn')
            logging.warning('Unvaild path. Using the default path[{0}].'.format(checked_path))
        if not Path(checked_path).exists():
            Path(checked_path).mkdir(parents=True)
            logging.info("The path[{0}] not existed. Creating.".format(str(checked_path)))
        return Path(checked_path)

    def _check_filepath(self) -> None:
        # check path and check file exists()
        self._conn_path = self._check_path(self._conn_path)
        self._conn_fpath = self._conn_path.joinpath(self.conf_filename)
        if not self._conn_fpath.exists():
            with open(self._conn_fpath, 'w') as f:
                json.dump({}, f)

    def _check_conn_dict(self) -> None:
        self.conf_dict = self.read_conf()
        conn_names = [f.name.replace('.txt', '') for f in list(self._conn_path.glob('*.txt'))]

        # check conn and conn_file
        # check conn_file in dict or not
        for conn_name in conn_names:
            if not self.conf_dict.get(conn_name):
                logging.warning('The file of connection[%s] not in conn_dict.' % conn_name)
                logging.warning('Remove the redundancy file.')
                Path(self._conn_path.joinpath(conn_name + ".txt")).unlink()

        # check conn in path or not
        for conn_name, fpath in self.conf_dict.items():
            # conn_name with file
            if conn_name in conn_names:
                if not Path(fpath).exists():
                    logging.warning(
                        'The file of connection[%s] in conn_dict is wrong.' % conn_name)
                    logging.warning('Fix the filepath.')
                    self.conf_dict[conn_name] = str(self._conn_path.joinpath(conn_name + ".txt"))
            # conn_name with no file
            else:
                logging.warning('The file of connection[%s] not exists.' % conn_name)
                logging.warning('Remove the redundancy connection.')
                self.conf_dict.pop(conn_name)

        # update conf_dict
        self._write_conf()

    def read_conf(self):
        # read the conf file
        self._check_filepath()
        with open(self._conn_fpath) as f:
            data = f.read()
        self.conf_dict = json.loads(data) if data else {}
        logging.debug(self.conf_dict)
        return self.conf_dict

    def _write_conf(self):
        # write the conf file
        self._check_filepath()
        with open(self._conn_fpath, 'w') as f:
            json.dump(self.conf_dict, f)
        logging.debug(self.conf_dict)

    def run(self, inputed_code, conn_name):
        self.conf_dict = self.read_conf()
        # inputed_code in ['READ', 'ADD', 'UPDATE', 'DELETE', 'RENAME']
        if inputed_code == 'READ':
            # read the _conn_conf from conn_file
            with open(self.conf_dict[conn_name]) as file_obj:
                data = file_obj.read() if not self.__prikeyfile else Decrypt(
                    self.__prikeyfile, file_obj.read())
            logging.debug('data: %s', data)
            self._conn_conf = json.loads(data)
            return self._conn_conf
        elif inputed_code == 'ADD':
            # write the _conn_conf to conn_file and update self.conf_dict
            self._conn_conf = {
                'sqlalchemy.url': self._create_conn_url(),
            }
            self._write_conn(conn_name, self._conn_path)
            self.conf_dict[conn_name] = str(self._conn_path.joinpath(conn_name + ".txt"))
        elif inputed_code == 'UPDATE':
            # read the _conn_conf from conn_file and compare with inputed _conn_conf
            old_conf = self.read(self._conn_path.joinpath(conn_name + '.txt'))
            new_conf = {
                'sqlalchemy.url': self._create_conn_url(),
            }
            self._conn_conf = dict_compare(
                old_conf, new_conf, diff_autoadd=True)
            self._write_conn(conn_name, self._conn_path)
        elif inputed_code == 'DELETE':
            Path(self.conf_dict[conn_name]).unlink()
            self.conf_dict.pop(conn_name)
        elif inputed_code == 'RENAME':
            # input new name
            tip_words = 'Please input the NEW name for connection[{0}].'.format(conn_name)
            conn_renamed = input_default('localhost', tip_words)
            while set([conn_renamed]) & set([name for name, path in self.conf_dict.items()]):
                logging.info('The NEW name[%s] already USED. Please input a NEW ONE.' % conn_renamed)
                conn_renamed = input_default('localhost', tip_words)
            # rename the txt file of conn_name
            conn_name_filepath = Path(self.conf_dict[conn_name]).resolve().parent
            conn_renamed_filepath = Path(conn_name_filepath).joinpath(conn_renamed + '.txt')
            Path(self.conf_dict[conn_name]).rename(conn_renamed_filepath)
            # update dict
            self.conf_dict.pop(conn_name)
            self.conf_dict[conn_renamed] = str(conn_renamed_filepath)
            logging.info('Connection[{0}] renamed to {1}.'.format(conn_name, conn_renamed))

        self._write_conf()
        logging.info('FileManager run over.')

    def _write_conn(self, conn_name, conn_path):
        # write the _conn_conf to conn_file
        with open(conn_path.joinpath(conn_name + '.txt'), 'w') as file_obj:
            if self.__pubkeyfile:
                file_obj.write(Encrypt(self.__pubkeyfile, json.dumps(self._conn_conf)))
            else:
                json.dump(self._conn_conf, file_obj)

    def _create_conn_url(self):
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

    @property
    def conn_path(self) -> Path:
        return self._conn_path

    @conn_path.setter
    def conn_path(self, new_path):
        old_path = self._conn_path
        self._conn_path = self._check_path(new_path)
        if str(old_path) != str(self._conn_path):
            logging.info("""The default path of conffile changed.
            From old_path: {0}
            to new_path: {1}""".format(str(old_path), str(self._conn_path)))

    @property
    def conf_filename(self) -> str:
        return self._conf_filename

    @conf_filename.setter
    def conf_filename(self, new_name):
        if not isinstance(new_name, str):
            raise TypeError('Expected a string')
        old_name = self._conf_filename
        self._conf_filename = str(new_name)
        logging.info("""The filename of conffile changed.
        From old_name: {0}
        to new_name: {1}""".format(str(old_name), str(new_name)))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        # filename=os.path.basename(__file__) + '_' + time.strftime('%Y%m%d', time.localtime()) + '.log',
        # filemode='a',
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    how_manager_run = logging.debug("""
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
""")
    manager = ConnUI('D:\\')
    print(manager.fmgr.conn_path)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
