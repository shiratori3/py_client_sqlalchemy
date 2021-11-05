#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   template.py
@Author  :   Billy Zhou
@Time    :   2021/09/29
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[1]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

import time
import datetime

if __name__ == '__main__':
    from src.post.task_scripts import get_nums
    from src.post.task_scripts import change_pools
    from src.post.task_scripts import requests_to_excel
    from src.post.RequestManager import RequestManager

    # 控制区域
    if True:
        pass

        # 各模块控制开关， True 为开启， False 为关闭
        # to_count = True
        # to_count = False
        insert_to_db = True  # 计数入库
        to_count = True  # 计数
        to_change = True  # 切换池子
        to_excel = True  # 导出数据

        hour_now = datetime.datetime.now().strftime("%H")
        print(time.time())
        log.info("hour_now: {0}".format(hour_now))
        if True and int(hour_now) > 12:
            log.info("Morning is gone.")
            # 12:00:00 后不再切换池子及导出数据
            to_change = False
            to_excel = False
        else:
            log.info("Good morning.")

        if to_count:
            # 进度查询的控制开关
            query_test_all = True  # 测试-进度查询

        if to_excel:
            # 抽检日期范围，以天为单位，以本日为基数
            s_range = -3 if datetime.datetime.now().weekday() == 0 else -1
            e_range = 0

    # 实际执行区域
    if True:
        # 初始化
        request_mgr = RequestManager(cwdPath.joinpath('res\\dev\\conf'))
        request_mgr.read_conf('settings.yaml')

        if to_count:
            if insert_to_db:
                from src.manager.EngineManager import EngineManager
                from src.utils.sql import sql_query

                manager = EngineManager()
                manager.read_conn_list()
                manager.set_engine('mysql_local', future=True, echo=False)
                engine_mysql = manager.get_engine('mysql_local')

            # 测试-进度查询
            if query_test_all:
                uncheck_nums = get_nums(
                    request_mgr,
                    cwdPath.joinpath('res\\dev\\task\\test_count.yaml')
                )
                log.info('unchecked: all: {}, push: {}'.format(uncheck_nums[0], uncheck_nums[1]))
                if insert_to_db and engine_mysql:
                    if uncheck_nums[0] is not False and uncheck_nums[1] is not False:
                        sql = 'INSERT INTO count_uncheck_test(`time_create`, `all`, `pushed`) VALUES (:t, :all, :pushed)'
                        bparams = {
                            't': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'all': uncheck_nums[0],
                            'pushed': uncheck_nums[1],
                        }
                        sql_query(engine_mysql, sql=sql, params_dict=bparams, commit_after=True, return_df=False)

        time.sleep(30) if to_count else time.sleep(1)
        if to_change:
            # 切换池子-测试
            change_pools(
                request_mgr,
                cwdPath.joinpath('res\\dev\\task\\test_poolchange.yaml')
            )

        time.sleep(10) if to_change else time.sleep(1)
        if to_excel:
            # 导出至excel
            requests_to_excel(
                request_mgr,
                cwdPath.joinpath('res\\dev\\task\\test_excel_uncheck.yaml'),
                day_range=[s_range, e_range]
            )
