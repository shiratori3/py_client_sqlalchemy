#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   num_count.py
@Author  :   Billy Zhou
@Time    :   2021/08/18
@Version :   1.6.0
@Desc    :   None
'''


import sys
import logging
import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2]))

from src.post.RequestParams import RequestParams  # noqa: E402


def num_count(request_params: RequestParams, payload_dicts: dict, diff_count=False):
    run_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info("Preparing requests at {}.".format(run_time))

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
    logging.info("responses get.")

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
            logging.info("total: %s", total)
            total_list.append(total)

    if diff_count:
        total_diff = total_list[0] - total_list[1]
        logging.info("total_diff: %s", total_diff)

    if total_success:
        return (run_time, total_list[0], total_list[1])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    request_params = RequestParams()
    request_params.read_conf('settings.yaml')

    run_time_1, uncheck_all, uncheck_pushed = num_count(
        request_params, {
            'query_juno_error_unfinished_2021.yaml': 'url',
            'getsql_juno_error_2021.yaml': 'urlgetSql',
        },
        diff_count=False
    )

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
