#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ErrorWordTemplate.py
@Author  :   Billy Zhou
@Time    :   2021/08/17
@Version :   1.0.0
@Desc    :   None
'''


import sys
import logging
from collections import Counter
from typing import List
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2]))

from src.manager.ConfManager import conf  # noqa: E402
from src.basic.sql_func import sql_read  # noqa: E402


class ErrorWordTemplate:
    def __init__(
            self,
            temp_fname: str = 'error_word_L.sql',
            temp_folder: Path = Path(conf.conf_dict['path']['confpath']).joinpath('docs\\sql_template'),
            sql_folder: Path = Path(conf.conf_dict['path']['confpath']).joinpath('docs\\sqlscript\\error_word')
    ) -> None:
        self.temp_fname = temp_fname
        self.temp_folder = Path(temp_folder)
        self.sql_folder = Path(sql_folder)
        if not self.temp_folder.exists:
            self.temp_folder.mkdir(parents=True)
        if not self.temp_folder.exists:
            self.temp_folder.mkdir(parents=True)
        self.sql_result = ''

    def read_template(self, temp_fname):
        if not Path(self.temp_folder).exists():
            raise ValueError('{} is not a vaild filepath.'.format(self.temp_folder))
        else:
            fpath = Path(self.temp_folder).joinpath(temp_fname)
            if not Path(fpath).exists():
                raise ValueError('{} is not a vaild filepath.'.format(fpath))
            else:
                self.sql_temp = sql_read(fpath)
                logging.debug("self.sql_temp: {!r}".format(self.sql_temp))
                return self.sql_temp

    def save_sql(self, sql_name: str):
        if not self.sql_result:
            raise ValueError('sql_result is blank')
        else:
            if not Path(self.sql_folder).exists():
                raise ValueError('{} is not a vaild filepath.'.format(self.sql_folder))
            else:
                fpath = Path(self.sql_folder).joinpath(sql_name)
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(self.sql_result)

    def create_error_word_sql(self, word_to_check: str, char_pairs: list = [], poi_pairs: List[tuple] = []):
        word_len = len(word_to_check)
        if word_len < 2:
            raise ValueError('word_to_check[{}] is too short.'.format(word_to_check))
        elif word_len <= 6:
            # use Short template
            self.read_template(temp_fname='error_word_S.sql')
            word_dict = {}
            for poi, char in enumerate(word_to_check, 1):
                word_dict[poi] = char
            # create the word list for check
            word_list = []
            if word_len < 4:
                for i in range(word_len):
                    word_concat = ''
                    for poi, char in word_dict.items():
                        word_concat += char if poi != i + 1 else '_'
                    word_list.append(word_concat)
                word_list += [''] * (4 - word_len)
                # append last element for +/-1
                word_list.append('[{}]'.format(word_to_check) if word_len == 2 else '[{w1}][{w2}]'.format(
                    w1=word_to_check[:2], w2=word_to_check[1:]))
            else:
                char_pairs = [word_to_check[:2], word_to_check[-2:]] if not char_pairs else char_pairs
                poi_pairs = set([])
                for i in range(4):
                    chars = ''.join([char_pairs[0][i // 2], char_pairs[1][i % 2]])
                    word_concat = ''
                    for poi, char in word_dict.items():
                        if char in chars:
                            word_concat += char
                            poi_pairs = poi_pairs | set([poi])
                        else:
                            word_concat += '_'
                    word_list.append(word_concat)
                # append last element for +/-1
                word_concat = ''
                for no, poi in enumerate(sorted(poi_pairs)):
                    while poi > len(word_concat.replace('[', '').replace(']', '')) + 1:
                        word_concat += '_'
                    if not no % 2:
                        word_concat += '['
                        word_concat += word_to_check[poi - 1]
                    else:
                        word_concat += word_to_check[poi - 1]
                        word_concat += ']'
                word_concat += '_' * (word_len - len(word_concat) + 4)
                word_list.append(word_concat)
            logging.info("word_list: {}".format(word_list))

            # delete -- according to the list length
            self.sql_temp_checked = self.sql_temp
            if word_len > 3:
                self.sql_temp_checked = self.sql_temp_checked.replace(
                    "--OR  A.DATA LIKE '{word_list[3", "OR  A.DATA LIKE '{word_list[3")
            if word_len > 2:
                self.sql_temp_checked = self.sql_temp_checked.replace(
                    "--OR  A.DATA LIKE '{word_list[2", "OR  A.DATA LIKE '{word_list[2")

            # create sql
            self.sql_result = self.sql_temp_checked.format(word_to_check=word_to_check, word_list=word_list)
            logging.debug("self.sql_result: {}".format(self.sql_result))
            self.save_sql(word_to_check + '.sql')
        elif word_len > 6:
            # use Long template
            self.read_template(temp_fname='error_word_L.sql')
            pairs_dict = {}
            if poi_pairs:
                for char, poi in zip(char_pairs, poi_pairs):
                    for i in range(len(char)):
                        pairs_dict[poi[i]] = char[i]
            else:
                need = Counter(''.join(char_pairs))
                for poi, char in enumerate(word_to_check):
                    if char in ''.join(char_pairs) and need[char] > 0:
                        pairs_dict[poi] = char
                        need[char] -= 1
            logging.debug("pairs_dict: {}".format(pairs_dict))
            pos_list = list(pairs_dict.keys())
            char_list = list(list(pairs_dict.values()))

            # delete -- according to the list length
            self.sql_temp_checked = self.sql_temp
            if len(pos_list) > 4:
                self.sql_temp_checked = self.sql_temp_checked.replace(
                    '--AND (SUBSTRING(A.DATA, {pos_list[4', 'AND (SUBSTRING(A.DATA, {pos_list[4')
            if len(pos_list) > 6:
                self.sql_temp_checked = self.sql_temp_checked.replace(
                    '--AND (SUBSTRING(A.DATA, {pos_list[6', 'AND (SUBSTRING(A.DATA, {pos_list[6')
            if len(pos_list) > 8:
                self.sql_temp_checked = self.sql_temp_checked.replace(
                    '--AND (SUBSTRING(A.DATA, {pos_list[7', 'AND (SUBSTRING(A.DATA, {pos_list[8')
            if len(pos_list) > 10:
                self.sql_temp_checked = self.sql_temp_checked.replace(
                    '--AND (SUBSTRING(A.DATA, {pos_list[10', 'AND (SUBSTRING(A.DATA, {pos_list[11')
            logging.debug("sql_temp_checked: {}".format(self.sql_temp_checked))

            # template sql only support input num equal to 12
            if len(pos_list) > 12:
                pos_list = pos_list[:12]
                char_list = char_list[:12]
            else:
                pos_list += [''] * (12 - len(pos_list))
                char_list += [''] * (12 - len(char_list))
            logging.info("pos_list: {}".format(pos_list))
            logging.info("char_list: {}".format(char_list))

            # create sql
            self.sql_result = self.sql_temp_checked.format(word_to_check=word_to_check, pos_list=pos_list, char_list=char_list)
            logging.debug("self.sql_result: {}".format(self.sql_result))
            self.save_sql(word_to_check + '.sql')

    @staticmethod
    def print_word_position(word: str) -> None:
        for poi, char in enumerate(word, 1):
            print('char[{0}] in position: {1}'.format(char, poi))
        print('word[{0}] splited over'.format(word))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        # filename=os.path.basename(__file__) + '_' + time.strftime('%Y%m%d', time.localtime()) + '.log',
        # filemode='a',
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    sqlTemp = ErrorWordTemplate()

    sqlTemp.create_error_word_sql('车辆')
    sqlTemp.create_error_word_sql('水电费')
    sqlTemp.create_error_word_sql('期间费用')
    sqlTemp.create_error_word_sql('可弥补亏损')
    sqlTemp.create_error_word_sql('股份支付费用', char_pairs=['股份', '支付'])

    word = '二、将重分类进损益的其他综合收益：权益法下可转损益的其他综合收益'
    sqlTemp.print_word_position(word)
    sqlTemp.create_error_word_sql(word, char_pairs=['将重', '可转', '合收'])
    sqlTemp.create_error_word_sql(
        word, char_pairs=['将重', '可转', '合收'], poi_pairs=[(3, 4), (22, 23), (30, 31)]
    )

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
