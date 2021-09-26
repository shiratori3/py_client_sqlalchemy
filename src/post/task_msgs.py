#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   task_msgs.py
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

from functools import wraps


def request_task_msgs(func):
    """A decorator to output additional msgs of request tasks"""
    @wraps(func)
    def wrapper(self, *args, url_type: str = 'url', task_name: str = '', **kwargs):
        response = func(self, *args, **kwargs)
        if response and isinstance(response, dict) and task_name:
            if url_type == 'url':
                log.info(f"{task_name} 执行成功")
            elif url_type == 'urlChange':
                log.info(f"{task_name} 切换成功")
            elif url_type == 'urlgetSql':
                log.info(f"{task_name} 执行成功")
                log.info("{} 总量: {}".format(task_name, response['data']['count']))
                log.info("{} 涉及公告数: {}".format(task_name, response['data']['influenceItemCount']))
                log.info("{} 涉及科目数: {}".format(task_name, response['data']['influenceSubjectCount']))
        return response
    return wrapper


if __name__ == '__main__':
    pass
