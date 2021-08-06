#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   encrypt.py
@Author  :   Billy Zhou
@Time    :   2021/08/06
@Version :   1.5.0
@Desc    :   None
'''

import os
import sys
import logging
import rsa
import base64
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2]))

from src.basic.add_gitignore import add_gitignore  # noqa: E402
from src.manager.ConfManager import cwdPath  # noqa: E402


def check_rsa_keys(savepath=cwdPath.joinpath('gitignore\\rsa')):
    add_gitignore('/gitignore/rsa/', under_gitignore=True)

    if not Path(savepath).is_dir():
        savepath = cwdPath.joinpath('gitignore\\rsa')
        logging.warning('Unvaild savepath. Save to default path(' + str(savepath) + ').')
        if not Path(savepath).exists():
            Path.mkdir(savepath, parents=True)

    pubkeyfile = Path(savepath).joinpath('public.pem')
    prikeyfile = Path(savepath).joinpath('private.pem')
    if not (Path(pubkeyfile).exists() and Path(prikeyfile).exists()):
        logging.warning('Keyfiles unfound. Creating under path(' + str(savepath) + ').')
        pubkeyfile, prikeyfile = create_rsa_keys(savepath)

    return pubkeyfile, prikeyfile


def create_rsa_keys(savepath):
    # 先生成一对密钥，然后保存.pem格式文件
    logging.info('Creating RSA keys.')
    (pubkey, privkey) = rsa.newkeys(2048)

    with open(savepath.joinpath('public.pem'), 'w+') as pubfile:
        logging.debug(type(pubkey.save_pkcs1()))
        pubfile.write(pubkey.save_pkcs1().decode('utf-8'))
    with open(savepath.joinpath('private.pem'), 'w+') as prifile:
        logging.debug(type(privkey.save_pkcs1()))
        prifile.write(privkey.save_pkcs1().decode('utf-8'))

    return savepath.joinpath('public.pem'), savepath.joinpath('private.pem')


def encrypt(pubkeyfile, data, savefile=''):
    if not isinstance(data, bytes):
        if os.path.isabs(data):
            if Path(data):
                if Path(data).is_file():
                    with open(data, encoding="utf-8") as df:
                        data = df.read()

    logging.debug('data_plain:')
    logging.debug(data)

    with open(pubkeyfile) as publicfile:
        pubkey = rsa.PublicKey.load_pkcs1(publicfile.read().encode('utf-8'))

        crypto = rsa.encrypt(data.encode('utf-8'), pubkey)
        crypto_decode_utf8 = base64.b64encode(crypto).decode('utf-8')
        logging.debug('cry: %s', crypto)  # bytes
        logging.debug('cry_base64: %s', base64.b64encode(crypto))  # bytes
        logging.debug('cry_base64_utf8: %s', crypto_decode_utf8)  # str
        logging.debug('data_encrypted: %s', crypto_decode_utf8)  # str

    if savefile:
        if not Path.exists(Path(savefile).parent):
            Path.mkdir(Path(savefile).parent, parents=True)

        with open(savefile, 'w+', encoding="utf-8") as sf:
            sf.write(crypto_decode_utf8)
    else:
        return crypto_decode_utf8


def decrypt(prikeyfile, data, savefile=''):
    if not isinstance(data, bytes) and os.path.isabs(data):
        if Path(data).is_file():
            with open(data, encoding="utf-8") as df:
                data = df.read()

    crypto_tra = base64.b64decode(data.encode('utf-8'))
    logging.debug('data_undecrypted: %s', data)  # str
    logging.debug('data: %s', data)  # str
    logging.debug('cry_utf8:  %s', data.encode('utf-8'))  # bytes
    logging.debug('cry_utf8_base64:  %s', crypto_tra)  # bytes

    with open(prikeyfile) as privatefile:
        privkey = rsa.PrivateKey.load_pkcs1(privatefile.read().encode('utf-8'))
        plaintext = rsa.decrypt(crypto_tra, privkey).decode('utf-8')

    if savefile:
        if not Path.exists(Path(savefile).parent):
            Path.mkdir(Path(savefile).parent, parents=True)
        with open(savefile, 'w+', encoding="utf-8") as sf:
            sf.write(plaintext)
    else:
        logging.debug('data_decrypted: %s', plaintext)
        return plaintext


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    # create test file
    with open(cwdPath.joinpath('rsa_test.txt'), 'a+') as test_file:
        test_file.seek(0, 0)  # back to the start
        f = test_file.read()
        logging.debug(f)
        if f == '':
            logging.info('测试文件为空')
            test_file.write('abc123456789')
    datafile = cwdPath.joinpath('rsa_test.txt')

    pubkeyfile, prikeyfile = check_rsa_keys()
    # pubkeyfile, prikeyfile = check_rsa_keys('rsa')

    # datafile_encrypted = cwdPath.joinpath('rsa_encrypted.txt')
    # datafile_decrypted = cwdPath.joinpath('rsa_decrypted.txt')
    # text_encrypted = encrypt(pubkeyfile, datafile, datafile_encrypted)
    # text_decryed = decrypt(
    #             prikeyfile, datafile_encrypted, datafile_decrypted)

    with open(datafile, encoding="utf-8") as df:
        data = df.read()
    text_encrypted = encrypt(pubkeyfile, data)
    text_decryed = decrypt(prikeyfile, text_encrypted)
    logging.info(text_decryed)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
