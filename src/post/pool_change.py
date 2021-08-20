#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   pool_change.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.Logger import logger  # noqa: E402
log = logger.get_logger(__name__)

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
            log.info("%s request执行成功", task_type)
        else:
            if task_type:
                task_type = task_type + '_'
            log.info(task_type + "总量: %s", response['data']['count'])
            log.info(task_type + "涉及公告数: %s", response['data']['influenceItemCount'])
            log.info(task_type + "涉及科目数: %s", response['data']['influenceSubjectCount'])


if __name__ == '__main__':
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
