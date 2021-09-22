#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   task_scripts.py
@Author  :   Billy Zhou
@Time    :   2021/09/22
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

import time
from typing import List
from src.manager.main import conf  # noqa: E402
from src.post.RequestManager import RequestManager  # noqa: E402
from src.basic.dataframe_func import records_to_df  # noqa: E402
from src.post.multi_requests import multi_requests_by_dicts  # noqa: E402
from src.post.multi_requests import multi_requests_increment  # noqa: E402


def change_pools(request_mgr: RequestManager, task_conf: Path) -> None:
    """change pools according to payload_confs in task_conf"""
    rq_dicts = conf.read_conf_from_file(task_conf, encoding='utf-8')
    log.debug(f"requests_dicts: {rq_dicts}")
    multi_requests_by_dicts(request_mgr, rq_dicts)


def get_nums(
        request_mgr: RequestManager, task_conf: Path,
        num_keys_mapping: dict = {'url': 'total', 'urlgetSql': 'count'}) -> list or None:
    """count nums of multi payload_conf

    Args:
    ----
        request_mgr: RequestManager
            a RequestManager instance
        task_conf: Path
            the path of conf for multi_requests_by_dicts
        num_keys_mapping:
            the dict of mapping url_type in requests_dicts to num_key

    Return:
    ------
        nums_list: list
            a list of the num of ['data']['total'] or such like key in responses
    """
    nums_list = []

    rq_dicts = conf.read_conf_from_file(task_conf)
    log.debug(f"requests_dicts: {rq_dicts}")
    responses_list = multi_requests_by_dicts(request_mgr, rq_dicts)

    total_success = True
    # get the nums in responses
    for task_name, records_list in responses_list.items():
        log.debug("length of responses_list.value: {}".format(len(records_list)))
        res = records_list[0]
        if isinstance(res, dict):
            num_type = num_keys_mapping[rq_dicts[task_name]['url_type']]
            if res['msg'] == '成功':
                log.debug("keys of responses_list.value[0]: {}".format(res.keys()))
                nums_list.append(int(res['data'][num_type]))
            else:
                nums_list.append(False)
                total_success = False
        else:
            log.error("error type of responses_list.value: {}".format(type(records_list)))
            total_success = False

    if total_success:
        return nums_list


def requests_to_excel(request_mgr: RequestManager, task_conf: Path, day_range: List[int] = []) -> None:
    """post to get responses and output the result to a excel file

    Args:
    ----
        request_mgr: RequestParams
            a RequestParams instance
        task_conf: Path
            the path of conf for multi_requests_by_dicts
        day_range: list, default []
            a list of two int to pass to request_mgr.read_payload

            For example, [-7, 0] meanings the date range between 7 days before and today
    """
    rq_dicts = conf.read_conf_from_file(task_conf, encoding='utf-8')
    log.debug("rq_dicts: {}".format(rq_dicts))

    for task_name, task_dict in rq_dicts.items():
        if not task_dict.get('task_vaild', True):
            if task_dict.get('task_name', ''):
                log.warning('The task[{}] is unvaild. Pass'.format(task_dict['task_name']))
        else:
            log.debug("task_dict of {}: {}".format(task_name, task_dict))
            # get args from task_dict
            excel_fpath = task_dict.get('excel_fpath', str(cwdPath.joinpath(
                task_name + '_{date}.yaml'))).format(
                    date=time.strftime("%Y%m%d-%H%M%S", time.localtime()))

            # get records_list
            records_list = multi_requests_increment(
                request_mgr, task_dict['conf_name'],
                max_limit=task_dict.get('max_limit', 10),
                day_range=day_range)

            # put records_list into excel
            if records_list:
                records_df = records_to_df(
                    records_list,
                    to_file=excel_fpath,
                    col_list_to_capture=task_dict.get('col_list_to_capture', []),
                    row_in_col_to_capture=task_dict.get('row_in_col_to_capture', {}),
                    row_in_col_to_discard=task_dict.get('row_in_col_to_discard', {}),
                    sample_num=task_dict.get('sample_num', 0),
                    timestamp_to_datetime=task_dict.get('timestamp_to_datetime', {})
                )
                log.debug("records_df: %s", records_df)
            else:
                log.warning("Blank records_list")


if __name__ == '__main__':
    request_mgr = RequestManager()
    request_mgr.read_conf('settings.yaml')

    if False:
        # test get_nums
        nums_list = get_nums(
            request_mgr,
            cwdPath.joinpath('conf\\task\\count_uncheck_tan.yaml')
        )
        log.info(nums_list)

    if False:
        # test change_pools
        change_pools(
            request_mgr,
            cwdPath.joinpath('conf\\task\\poolchange.yaml')
        )

    if False:
        # test requests_to_excel
        task_conf = cwdPath.joinpath('res\\dev\\test_conf.yaml')
        rq_dicts = conf.read_conf_from_file(task_conf, encoding='utf-8')
        log.debug("rq_dicts: {}".format(rq_dicts))

        requests_to_excel(
            request_mgr,
            cwdPath.joinpath('conf\\task\\excel_autofill_intercept.yaml')
        )
        requests_to_excel(
            request_mgr,
            cwdPath.joinpath('conf\\task\\excel_autofill_sample.yaml'),
            day_range=[-7, 0]
        )
