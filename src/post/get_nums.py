#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   get_nums.py
@Author  :   Billy Zhou
@Time    :   2021/09/18
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

from src.manager.main import conf  # noqa: E402
from src.post.RequestManager import RequestManager  # noqa: E402
from src.post.multi_requests import multi_requests_by_dicts  # noqa: E402


def get_nums(request_mgr: RequestManager, task_conf: Path, num_keys_mapping: dict = {'url': 'total', 'urlgetSql': 'count'}):
    """count nums of multi payload_conf

    Args:
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


if __name__ == '__main__':
    request_mgr = RequestManager()
    request_mgr.read_conf('settings.yaml')

    if True:
        # test get_nums
        nums_list = get_nums(
            request_mgr,
            cwdPath.joinpath(cwdPath.joinpath('conf\\task\\count_uncheck_tan.yaml'))
        )
        log.info(nums_list)
