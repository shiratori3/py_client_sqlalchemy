#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   conn_manager.py
@Author  :   Billy Zhou
@Time    :   2021/06/15
@Version :   1.0.0
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
        handle_type='',
        conn_path=cwdPath.joinpath('gitignore\\conn')):
    # read json file of connections
    json_dict = manage_conn_json('READ', conn_path=conn_path)
    if json_dict:
        conn_list = [name for name, path in json_dict.items()]
        conn_list_str = '"' + '",  "'.join(conn_list) + '"'
        print('Existed connections: ' + conn_list_str)
    else:
        conn_list = []
        conn_name_selected = ''
        print('No existing connection.')

    handle_list = ['read', 'add', 'update', 'delete', 'clear', 'rename']
    if handle_type.upper() not in [i.upper() for i in handle_list]:
        print('Invaild handle_type. Using the default handle_list.')
        selection = input_checking_list(handle_list, 'Please choose your operation.')
    else:
        selection = handle_type.upper()

    if selection in ['READ', 'ADD', 'UPDATE', 'DELETE', 'RENAME']:
        if not conn_list or selection == 'ADD':
            if selection != 'ADD':
                tip_words = 'No existing connection to ' + selection + '. Add a new one?'
                selection_add = input_checking_YN(tip_words)
                if selection_add == 'Y':
                    selection = 'ADD'
                else:
                    print('Canceled.')
                    selection = 'PASS'

            if selection == 'ADD':
                conn_name_selected = input_default('localhost', 'Please input the connection name to ADD.')
                # check exist or not
                if conn_list and conn_name_selected in conn_list:
                    tip_words = 'Connection[{0}] already existed. Update it?'.format(conn_name_selected)
                    selection_update = input_checking_YN(tip_words)
                    if selection_update == 'Y':
                        selection = 'UPDATE'
                    else:
                        print('Canceled.')
                        selection = 'PASS'
        else:
            tip_words = 'Please choose the connection to ' + selection + '.'
            conn_name_selected = input_checking_list(conn_list, tip_words, case_sens=True)

        conn_info = manage_conn_info(
            handle_type=selection, json_dict=json_dict,
            conn_name=conn_name_selected, conn_path=conn_path)
        if conn_info and selection == 'READ':
            print('conn_info: %s' % conn_info)
            return conn_info
    elif selection == 'CLEAR':
        tip_words = 'Attension! This will delete all existing connections. Are you sure?'
        selection_clear = input_checking_YN(tip_words, default_Y=False)
        if selection_clear == 'Y':
            selection = 'DELETE'
            for conn_name_selected in conn_list:
                conn_info = manage_conn_info(
                    handle_type=selection, json_dict=json_dict,
                    conn_name=conn_name_selected, conn_path=conn_path)
            print('Cleared.')
        else:
            print('Canceled.')


def manage_conn_json(
        handle_type, conn_path,
        conn_name='', json_dict_updated={}):
    # handle_type in ['READ', 'ADD', 'UPDATE', 'DELETE', 'RENAME']
    # get dict of connection info
    if not Path(conn_path).is_dir():
        conn_path = cwdPath.joinpath('gitignore\\conn')
        print('Unvaild conn_path. Using the default path(' + str(conn_path) + ').')
        if not Path(conn_path).exists():
            Path.mkdir(conn_path, parents=True)
    json_path = conn_path.joinpath('conn_info.json')
    json_dict = {}
    if not json_path.exists():
        with open(json_path, 'w') as f:
            json.dump({}, f)
    if handle_type == 'READ':
        with open(json_path) as f:
            data = f.read()
            if data:
                json_dict = json.loads(data)
        logging.debug(json_dict)
        return json_dict
    else:
        if handle_type == 'ADD':
            print('Connection[%s] added.' % conn_name)
        elif handle_type == 'RENAME':
            # rename
            tip_words = 'Please input the NEW name for connection[{0}].'.format(conn_name)
            conn_renamed = input_default('localhost', tip_words)
            while set([conn_renamed]) & set([name for name, path in json_dict_updated.items()]):
                print('The NEW name[%s] already USED. Please input again.' % conn_renamed)
                conn_renamed = input_default('localhost', tip_words)
            # rename the txt file of conn_name
            conn_name_filepath = Path(json_dict_updated[conn_name]).resolve().parent
            conn_renamed_filepath = Path(conn_name_filepath).joinpath(conn_renamed + '.txt')
            Path(json_dict_updated[conn_name]).rename(conn_renamed_filepath)
            # update dict
            json_dict_updated.pop(conn_name)
            json_dict_updated[conn_renamed] = str(conn_renamed_filepath)
            print('Connection[{0}] renamed to {1}.'.format(conn_name, conn_renamed))
        elif handle_type == 'UPDATE':
            json_dict_updated = dict_compare(
                json_dict, json_dict_updated, diff_autoadd=True)
            print('Connection[%s] updated.' % conn_name)
        elif handle_type == 'DELETE':
            if Path(json_dict_updated[conn_name]).exists():
                Path(json_dict_updated[conn_name]).unlink()
                json_dict_updated.pop(conn_name)
            else:
                print('The file of connection[%s] not exist. Drop it.' % conn_name)
                json_dict_updated.pop(conn_name)
            print('Connection[%s] deleted.' % conn_name)

        with open(json_path, 'w') as f:
            json.dump(json_dict_updated, f)

        logging.debug(json_dict_updated)
        return json_dict_updated


def manage_conn_info(
        handle_type, json_dict, conn_name, conn_path,
        encrypt=True):
    # handle_type in ['READ', 'ADD', 'UPDATE', 'DELETE', 'RENAME', 'PASS']
    if handle_type == 'PASS':
        return False
    else:
        add_gitignore('/gitignore/conn/', under_gitignore=True)
        pubkeyfile, prikeyfile = CheckRSAKeys(encrypt)
        conn_info = {}
        json_dict_readed = json_dict

        # connection called conn_name exist or not
        if handle_type in ['ADD'] and not json_dict.get(conn_name):
            print('Connection[%s] not existed. Creating a new connection.' % conn_name)
            conn_info = create_conn_info(
                conn_name, conn_path, json_dict_readed, encrypt, pubkeyfile)
        else:
            if handle_type in ['UPDATE']:
                print('Updating existing connection[%s].' % conn_name)
                conn_info = create_conn_info(
                    conn_name, conn_path, json_dict_readed, encrypt, pubkeyfile)
            elif handle_type in ['READ']:
                print('Reading existing connection[%s].' % conn_name)
                with open(json_dict[conn_name]) as file_obj:
                    if encrypt and prikeyfile:
                        data = Decrypt(prikeyfile, file_obj.read())
                    else:
                        data = file_obj.read()
                logging.debug('data: %s', data)
                conn_info = json.loads(data)

        if handle_type in ['ADD', 'UPDATE', 'DELETE', 'RENAME']:
            # update json_dict
            manage_conn_json(
                handle_type, conn_path=conn_path, conn_name=conn_name,
                json_dict_updated=json_dict_readed)

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

    conn = conn_manager()

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
