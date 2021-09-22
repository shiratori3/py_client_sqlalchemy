#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Crypt.py
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

import os
import rsa
import base64
from src.manager.Ignorer import Ignorer  # noqa: E402


class Crypt:
    """encrypt and decrypt str using rsa algorithm

    Attrs:
        savepath: Path, default cwdPath.joinpath('conf\\rsa')
            the directory to save pubkeyfile and prikeyfile if pubkeyfile or prikeyfile unvaild
        pubkeyfile: Path, default cwdPath.joinpath('conf\\rsa').joinpath('public.pem')
            the filepath of pubkeyfile
        prikeyfile: Path, default cwdPath.joinpath('conf\\rsa').joinpath('private.pem')
            the filepath of prikeyfile
        gitignorer: Ignorer, default None
            a instance of Ignorer. If none, create a new one

    Methods:
        check_rsa_keys(self):
            check whether self.pubkeyfile and self.prikeyfile is vaild. If unvaild, create new ones under savepath
        create_rsa_keys(self):
            create a pair of rsa keys and then save to .pem file under savepath
        encrypt(self, data: str or bytes, savefile: Path = '', pubkeyfile: Path = ''):
            encrypt the data and return the encrypted data or write into savefile
        decrypt(self, data: str or bytes, savefile: Path = '', prikeyfile: Path = ''):
            decrypt the data and return the decrypted data or write into savefile
    """
    def __init__(
            self, savepath: Path = cwdPath.joinpath('conf\\rsa'),
            pubkeyfile: Path = cwdPath.joinpath('conf\\rsa').joinpath('public.pem'),
            prikeyfile: Path = cwdPath.joinpath('conf\\rsa').joinpath('private.pem'),
            gitignorer: Ignorer = None
    ) -> None:
        self.savepath = savepath
        self.pubkeyfile = pubkeyfile
        self.prikeyfile = prikeyfile

        # check ignore
        if not gitignorer:
            self._gitignorer = Ignorer()
        if gitignorer:
            self._gitignorer = gitignorer
            if Path(savepath) == cwdPath.joinpath('conf\\rsa'):
                self._gitignorer.add_gitignore('/conf/rsa/')
            else:
                self._gitignorer.add_gitignore(str(savepath))

        # check rsa_keys
        self.check_rsa_keys()

        log.debug('Crypt inited')

    def check_rsa_keys(self):
        """check whether self.pubkeyfile and self.prikeyfile is vaild. If unvaild, create new ones under savepath"""
        if not (Path(self.pubkeyfile).exists() and Path(self.prikeyfile).exists()):
            log.warning('Keyfiles unfound. Creating under path[{}].'.format(self.savepath))

            if not Path(self.savepath).exists():
                log.warning('Unvaild savepath. Use the default path[{}].'.format(self.savepath))
                self.savepath = cwdPath.joinpath('conf\\rsa')
                Path.mkdir(self.savepath, parents=True)
            self.pubkeyfile, self.prikeyfile = self._create_rsa_keys()

        return self.pubkeyfile, self.prikeyfile

    def _create_rsa_keys(self):
        """create a pair of rsa keys and then save to .pem file under savepath"""
        log.info('Creating RSA keys.')
        (pubkey, privkey) = rsa.newkeys(2048)

        with open(self.savepath.joinpath('public.pem'), 'w+') as pubfile:
            pubfile.write(pubkey.save_pkcs1().decode('utf-8'))
        with open(self.savepath.joinpath('private.pem'), 'w+') as prifile:
            prifile.write(privkey.save_pkcs1().decode('utf-8'))

        return self.savepath.joinpath('public.pem'), self.savepath.joinpath('private.pem')

    def encrypt(self, data: str or bytes, savefile: Path = '', pubkeyfile: Path = ''):
        """encrypt the data and return the encrypted data or write into savefile

        Args:
            data: str or bytes
                data to encrypt, can be a filepath
            savefile: Path, optional, default ''
                the path to save the encrypted data
            pubkeyfile: Path,  optional, default ''
                the path of pubkeyfile. use pubkeyfile instead of self.pubkeyfile to encrypt
        """
        # if data is a filepath, read the content in file
        data = self.__check_data_type(data) if self.__check_data_type(data) else data

        pubkeyfile = self.pubkeyfile if not pubkeyfile else pubkeyfile
        with open(self.pubkeyfile) as publicfile:
            pubkey = rsa.PublicKey.load_pkcs1(publicfile.read().encode('utf-8'))
            crypto = rsa.encrypt(data.encode('utf-8'), pubkey)
            encrypted = base64.b64encode(crypto).decode('utf-8')
            log.debug('cry: %s', crypto)  # bytes
            log.debug('data_encrypted: %s', base64.b64encode(crypto).decode('utf-8'))  # str

        return encrypted if not savefile else self.__save_to_file(savefile, encrypted)

    def decrypt(self, data: str or bytes, savefile: Path = '', prikeyfile: Path = ''):
        """decrypt the data and return the decrypted data or write into savefile

        Args:
            data: str or bytes
                data to decrypt, can be a filepath
            savefile: Path, optional, default ''
                the path to save the decrypted data
            prikeyfile: Path,  optional, default ''
                the path of prikeyfile. use prikeyfile instead of self.prikeyfile to decrypt
        """
        # if data is a filepath, read the content in file
        data = self.__check_data_type(data) if self.__check_data_type(data) else data

        prikeyfile = self.prikeyfile if not prikeyfile else prikeyfile
        with open(self.prikeyfile) as privatefile:
            privkey = rsa.PrivateKey.load_pkcs1(privatefile.read().encode('utf-8'))
            crypto_tra = base64.b64decode(data.encode('utf-8'))
            plaintext = rsa.decrypt(crypto_tra, privkey).decode('utf-8')
            log.debug('data_undecrypted: %s', data)  # str
            log.debug('cry_utf8_base64:  %s', crypto_tra)  # bytes

        log.debug('data_decrypted: %s', plaintext)
        return plaintext if not savefile else self.__save_to_file(savefile, plaintext)

    @staticmethod
    def __check_data_type(data: str or bytes):
        """if inputed data is a filepath, read it"""
        if not isinstance(data, bytes) and os.path.isabs(data):
            if Path(data).is_file():
                with open(data, encoding="utf-8") as df:
                    data = df.read()
                return data

    @staticmethod
    def __save_to_file(fpath: Path, data: str or bytes):
        """save the data to fpath"""
        if not Path.exists(Path(fpath).parent):
            Path.mkdir(Path(fpath).parent, parents=True)
        with open(Path(fpath), 'w+', encoding="utf-8") as sf:
            sf.write(data)
        return Path(fpath)


if __name__ == '__main__':
    # init
    gitignorer = Ignorer()
    crypter = Crypt(gitignorer=gitignorer)

    pubkeyfile, prikeyfile = crypter.check_rsa_keys()

    # create test file
    datafile = cwdPath.joinpath('res\\dev\\rsa_test.txt')
    with open(datafile, 'a+') as test_file:
        test_file.seek(0, 0)  # back to the start
        f = test_file.read()
        log.debug("content in file: {}".format(f))
        if f == '':
            log.info('测试文件为空')
            test_file.write('abc123456789')

    # testing 1
    with open(datafile, encoding="utf-8") as df:
        data = df.read()
    text_encrypted = crypter.encrypt(data)
    log.info("text_encrypted: {}".format(text_encrypted))
    text_decryed = crypter.decrypt(text_encrypted, cwdPath.joinpath('res\\dev\\rsa_decryed.txt'))
    log.info("text_decryed: {}".format(text_decryed))

    # testing 2
    text_encrypted = crypter.encrypt(datafile, cwdPath.joinpath('res\\dev\\rsa_encrypted.txt'))
    log.info("text_encrypted: {}".format(text_encrypted))
    text_decryed = crypter.decrypt(text_encrypted)
    log.info("text_decryed: {}".format(text_decryed))
