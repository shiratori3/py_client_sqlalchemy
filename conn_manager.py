#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   conn_manager.py
@Author  :   Billy Zhou
@Time    :   2021/06/14
@Version :   0.5.0
@Desc    :   None
'''


import logging
import json
from pathlib import Path


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


def conn_manager(
        handle_type='read',
        conn_path=cwdPath.joinpath('gitignore\\conn')):
    handle_list = ['read', 'add', 'update', 'delete', 'clear', 'rename']
    if handle_type.upper() not in [i.upper() for i in handle_list]:
        print('Invaild handle_type. Using the default handle_list.')
        selection = input_checking_list(handle_list, 'Please choose your operation.')
    else:
        selection = handle_type.upper()

    if selection in ['READ', 'ADD', 'UPDATE']:
        json_dict = manage_conn_json(conn_path=conn_path)
        if json_dict:
            conn_list = [name for name, path in json_dict.items()]
        else:
            print('No exist vaild connection info.')
        if conn_list and selection == 'READ':
            conn_name_selected = input_checking_list(conn_list, 'Please choose connection to read.')
        elif conn_list and selection == 'UPDATE':
            conn_name_selected = input_checking_list(conn_list, 'Please choose connection to update.')
        else:
            conn_name_selected = input_default('localhost', 'Please input the connection name to add.')
        conn_info = manage_conn_info(handle_type=selection, conn_name=conn_name_selected)

        if selection == 'READ':
            print('conn_info: %s' % conn_info)
    elif selection == 'DELETE':
        pass
    elif selection == 'CLEAR':
        pass
    elif selection == 'RENAME':
        pass


def manage_conn_json(
        handle_type='READ', conn_name='',
        conn_path=cwdPath.joinpath('gitignore\\conn'),
        json_dict_updated={}):
    if not Path(conn_path).is_dir():
        conn_path = cwdPath.joinpath('gitignore\\conn')
        print('Unvaild conn_path. Using the default path(' + str(conn_path) + ').')
        if not Path(conn_path).exists():
            Path.mkdir(conn_path, parents=True)
    json_dict = {}

    # get dict of connection info
    json_path = conn_path.joinpath('conn_info.json')
    if not json_path.exists():
        with open(json_path, 'w') as f:
            json.dump({}, f)
    with open(json_path) as f:
        data = f.read()
        if data:
            json_dict = json.loads(data)

    if json_dict_updated and handle_type in ('WRITE', 'UPDATE'):
        if handle_type == 'UPDATE':
            json_dict_updated = dict_compare(
                json_dict, json_dict_updated, diff_autoadd=True)
        with open(json_path, 'w') as f:
            json.dump(json_dict_updated, f)
    elif handle_type == 'DELETE':
        pass
    elif handle_type == 'RENAME':
        pass

    logging.debug(json_dict)
    return json_dict


def manage_conn_info(
        handle_type='READ', conn_name='',
        conn_path=cwdPath.joinpath('gitignore\\conn'),
        encrypt=True):
    add_gitignore('/gitignore/conn/', under_gitignore=True)
    pubkeyfile, prikeyfile = CheckRSAKeys(encrypt)

    # get dict of connection info
    json_dict = manage_conn_json(conn_path=conn_path)

    # connection called conn_name exist or not
    if not json_dict.get(conn_name):
        print('Connection not exist. Creating a new connection')
        conn_info = create_conn_info(conn_name, conn_path, json_dict, encrypt, pubkeyfile)
    else:
        print('Opening existing connection.')
        with open(json_dict[conn_name]) as file_obj:
            if encrypt and prikeyfile:
                data = Decrypt(prikeyfile, file_obj.read())
            else:
                data = file_obj.read()
        logging.debug('data: %s', data)
        conn_info = json.loads(data)

    manage_conn_json(
        'WRITE', conn_path=conn_path, json_dict_updated=json_dict)

    logging.debug(conn_info)
    return conn_info


def create_conn_info(conn_name, conn_path, json_dict, encrypt=False, pubkeyfile=''):
    conn_info = {
        'host': input_default('localhost', 'Please input host: '),
        'database': input_default('master', 'Please input database: '),
        'user': input_default('sa', 'Please input username: '),
        'pwd': input_pwd().strip(),
    }

    update_conn_info(conn_info, conn_name, conn_path, json_dict, encrypt, pubkeyfile)

    logging.debug(conn_info)
    return conn_info


def update_conn_info(conn_info, conn_name, conn_path, json_dict, encrypt=False, pubkeyfile=''):
    print('Saving the info of connection to ' + conn_name + '.txt')
    with open(conn_path.joinpath(conn_name + '.txt'), 'w') as file_obj:
        if encrypt and pubkeyfile:
            file_obj.write(Encrypt(pubkeyfile, json.dumps(conn_info)))
        else:
            json.dump(conn_info, file_obj)
        json_dict[conn_name] = str(conn_path.joinpath(conn_name + '.txt').resolve())


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    # conn = manage_conn_info()

    conn = manage_conn_info(
        'localhost', encrypt=True)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
