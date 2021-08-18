#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ErrorWordTemplate.py
@Author  :   Billy Zhou
@Time    :   2021/08/17
@Version :   1.0.2
@Desc    :   None
'''


import sys
import logging
from collections import Counter
from typing import List
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2]))

from src.manager.ConfManager import conf  # noqa: E402
from src.sql_template.SqlTemplate import SqlTemplate  # noqa: E402


class ErrorWordTemplate(SqlTemplate):
    def __init__(
            self,
            temp_fname: str = 'error_word_L.sql',
            temp_folder: Path = Path(conf.conf_dict['path']['confpath']).joinpath('docs\\sql_template'),
            sql_folder: Path = Path(conf.conf_dict['path']['confpath']).joinpath('docs\\sqlscript\\error_word')
    ) -> None:
        super().__init__(temp_folder=temp_folder, sql_folder=sql_folder)
        self.temp_fname = temp_fname

    def create_sql(self, word_to_check: str, char_pairs: list = [], poi_pairs: List[tuple] = []):
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

    word_sql = ErrorWordTemplate()

    word_sql.create_sql('车辆')
    word_sql.create_sql('水电费')
    word_sql.create_sql('期间费用')
    word_sql.create_sql('可弥补亏损')
    word_sql.create_sql('股份支付费用', char_pairs=['股份', '支付'])

    word = '二、将重分类进损益的其他综合收益：权益法下可转损益的其他综合收益'
    word_sql.print_word_position(word)
    word_sql.create_sql(word, char_pairs=['将重', '可转', '合收'])
    word_sql.create_sql(
        word, char_pairs=['将重', '可转', '合收'], poi_pairs=[(3, 4), (22, 23), (30, 31)]
    )

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
