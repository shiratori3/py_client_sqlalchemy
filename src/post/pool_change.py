#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   pool_change.py
@Author  :   Billy Zhou
@Time    :   2021/08/18
@Version :   1.6.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2]))

from src.post.RequestParams import RequestParams  # noqa: E402


def pool_change(request_params: RequestParams, payload_conf: str, url_type: str = 'urlChange', task_type: str = ''):
    request_params.read_payload(payload_conf, show_payload=False, no_page=True)
    response = request_params.send_request(
        'POST',
        url=request_params.read_url(url_type),
        payload_from_conf=payload_conf
    )
    if response and isinstance(response, dict):
        if url_type == 'urlChange':
            logging.info("%s request执行成功", task_type)
        else:
            if task_type:
                task_type = task_type + '_'
            logging.info(task_type + "总量: %s", response['data']['count'])
            logging.info(task_type + "涉及公告数: %s", response['data']['influenceItemCount'])
            logging.info(task_type + "涉及科目数: %s", response['data']['influenceSubjectCount'])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    request_params = RequestParams()
    request_params.read_conf('settings.yaml')

    pool_change(
        request_params,
        payload_conf='poolchange_juno_error_inner.yaml',
        url_type='urlgetSql', task_type='内部专项校验错误-全量'
    )
    # pool_change(
    #     request_params,
    #     payload_conf='poolchange_juno_error_inner.yaml',
    #     url_type='urlChange', task_type='内部专项校验错误-全量'
    # )

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
