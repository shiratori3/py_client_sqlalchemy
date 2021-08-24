#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   num_count.py
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

import datetime
from src.post.RequestParams import RequestParams  # noqa: E402


def num_count(request_params: RequestParams, payload_dicts: dict, diff_count: bool = False):
    """count nums of multi payload_conf

    Args:
        request_params: RequestParams
            a RequestParams instance
        payload_dicts: dict
            a dict of pairs of payload_conf_fname and url_type to read from RequestParams,
            format: 'payload_conf_fname': 'url_type'

            For example, {
                'query_juno_error_unfinished_2021.yaml': 'url',
                'getsql_juno_error_2021.yaml': 'urlgetSql',
            }
        diff_count: bool, default False
            whether to calculate the diff between payload_confs
    """
    run_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log.info("Preparing requests at {}.".format(run_time))

    response_list = []
    url_type_list = []
    for conf, url_type in payload_dicts.items():
        # put responses of requests to response_list
        request_params.read_payload(conf, show_payload=False, no_page=False)
        response_list.append(
            request_params.send_request(
                "POST", url=request_params.read_url(url_type),
                payload_from_conf=conf
            )
        )
        url_type_list.append(url_type)
    log.info("responses get.")

    total_list = []
    total_success = True
    url_mapping = {'url': 'total', 'urlgetSql': 'count'}
    for no, r in enumerate(response_list):
        # get nums in response_list
        if isinstance(r, dict):
            if r['msg'] == '成功':
                total = int(r['data'][url_mapping[url_type_list[no]]])
            else:
                total = False
                total_success = False
            log.info("total: %s", total)
            total_list.append(total)

    if diff_count:
        total_diff = total_list[0] - total_list[1]
        log.info("total_diff: %s", total_diff)

    if total_success:
        return (run_time, total_list[0], total_list[1])


if __name__ == '__main__':
    request_params = RequestParams()
    request_params.read_conf('settings.yaml')

    run_time_1, uncheck_all, uncheck_pushed = num_count(
        request_params, {
            'query_juno_error_unfinished_2021.yaml': 'url',
            'getsql_juno_error_2021.yaml': 'urlgetSql',
        },
        diff_count=False
    )
