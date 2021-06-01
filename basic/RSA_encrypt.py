#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   RSA_encrypt.py
@Author  :   Billy Zhou
@Time    :   2021/03/12
@Version :   1.2.0
@Desc    :   None
'''

import os
import sys
import logging
import rsa
import base64
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from conf_manage import readConf  # noqa: E402
cwdPath = Path(readConf()["path"]['cwd'])


def CheckRSAKeys(savepath=''):
    # 对应文件夹是否存在
    if Path(savepath) != Path('') and Path(savepath).is_dir():
        savepath = Path(savepath)
    else:
        print('Error. Unvaild Path. Will save to default path')
        savepath = cwdPath.joinpath('gitignore\\rsa')
    logging.debug(savepath)
    if not Path(savepath).exists():
        Path.mkdir(savepath, parents=True)

    kfdict = {
        'pubfile': savepath.joinpath('public.pem'),
        'prifile': savepath.joinpath('private.pem'),
    }
    if not (kfdict['pubfile'].exists() and kfdict['prifile'].exists()):
        kfdict = CreateRSAKeys(savepath)

    # git上传忽略对应文件
    with open(cwdPath.joinpath('.gitignore'), 'a+', encoding='utf-8') as f:
        rsa_ignore = False
        f.seek(0, 0)  # back to the start
        for i in f.readlines():
            logging.debug(i.replace('\n', ''))
            if i.replace('\n', '') in ['/gitignore/', '/gitignore/rsa/']:
                rsa_ignore = True
                break
        if not rsa_ignore:
            f.write('\n/gitignore/rsa/\n')
    return kfdict['pubfile'], kfdict['prifile']


def CreateRSAKeys(savepath):
    # 先生成一对密钥，然后保存.pem格式文件
    print('Creating RSA keys.')
    (pubkey, privkey) = rsa.newkeys(2048)

    with open(savepath.joinpath('public.pem'), 'w+') as pubfile:
        logging.debug(type(pubkey.save_pkcs1()))
        pubfile.write(pubkey.save_pkcs1().decode('utf-8'))
    with open(savepath.joinpath('private.pem'), 'w+') as prifile:
        logging.debug(type(privkey.save_pkcs1()))
        prifile.write(privkey.save_pkcs1().decode('utf-8'))

    return {
        'pubfile': savepath.joinpath('public.pem'),
        'prifile': savepath.joinpath('private.pem'),
    }


def Encrypt(pubkeyfile, data, savefile=''):
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


def Decrypt(prikeyfile, data, savefile=''):
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

    pubkeyfile, prikeyfile = CheckRSAKeys(
        cwdPath.joinpath('gitignore\\rsa'))

    # datafile_encrypted = cwdPath.joinpath('rsa_encrypted.txt')
    # datafile_decrypted = cwdPath.joinpath('rsa_decrypted.txt')
    # text_encrypted = Encrypt(pubkeyfile, datafile, datafile_encrypted)
    # text_decryed = Decrypt(
    #             prikeyfile, datafile_encrypted, datafile_decrypted)

    with open(datafile, encoding="utf-8") as df:
        data = df.read()
    text_encrypted = Encrypt(pubkeyfile, data)
    text_decryed = Decrypt(prikeyfile, text_encrypted)
    logging.info(text_decryed)

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
