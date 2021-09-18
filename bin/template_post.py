#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   template.py
@Author  :   Billy Zhou
@Time    :   2021/09/18
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
    from src.post.get_nums import get_nums
    from src.post.pool_change import pool_change
    from src.post.requests_to_excel import requests_to_excel
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

        if to_change:
            # 切换池子的控制开关
            poolchange_test = True  # 测试
            poolchange_test_2021 = True  # 测试-2021

        if to_excel:
            # 对应数据导出的控制开关
            # 全量均不包含失效或已暂停的数据
            excel_test = True  # 测试

            # 抽检日期范围，以天为单位，以本日为基数
            s_range = -3 if datetime.datetime.now().weekday() == 0 else -1
            e_range = 0

    # 实际执行区域
    if True:
        # 初始化
        request_mgr = RequestManager()
        request_mgr.read_conf('settings.yaml')

        if to_count:
            if insert_to_db:
                from src.manager.EngineManager import EngineManager
                from src.basic.sql_func import sql_query

                manager = EngineManager()
                manager.read_conn_list()
                manager.set_engine('mysql_local', future=True, echo=False)
                engine_mysql = manager.get_engine('mysql_local')

            # 测试-进度查询
            if query_test_all:
                run_time_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                uncheck_nums = get_nums(
                    request_mgr,
                    cwdPath.joinpath('conf\\task\\count_uncheck.yaml')
                )
                log.info('unchecked: all: {}, push: {}'.format(uncheck_nums[0], uncheck_nums[1]))
                if insert_to_db and engine_mysql:
                    if uncheck_nums[0] is not False and uncheck_nums[1] is not False:
                        sql = 'INSERT INTO count_uncheck(`time_create`, `all`, `pushed`) VALUES (:t, :all, :pushed)'
                        bparams = {
                            't': run_time_1,
                            'all': uncheck_nums[0],
                            'pushed': uncheck_nums[1],
                        }
                        sql_query(engine_mysql, sql=sql, params_dict=bparams, commit_after=True, return_df=False)

        time.sleep(30) if to_count else time.sleep(1)
        if to_change:
            # 切换池子-测试-2021
            if run_time_1 and poolchange_test_2021:
                pool_change(
                    request_mgr,
                    payload_conf='poolchange_uncheck_2021.yaml',
                    url_type='change', task_type='测试'
                )
                time.sleep(2)

            # 切换池子-测试-all
            if poolchange_test:
                pool_change(
                    request_mgr,
                    payload_conf='poolchange_uncheck.yaml',
                    url_type='change', task_type='测试-all'
                )
                time.sleep(2)

        time.sleep(10) if to_change else time.sleep(1)
        if to_excel:
            if excel_test:
                # 测试-全量
                requests_to_excel(
                    request_mgr,
                    payload_conf='excel\\excel_test.yaml',
                    excel_fpath='D:\\测试_{date}.xlsx'.format(
                        date=time.strftime("%Y%m%d-%H%M%S", time.localtime())),
                    col_list=['id', ],  # 根据需要的字段自行调整
                    max_page=100,
                    row_in_col_to_capture={},
                    row_in_col_to_discard={},
                    day_range=[s_range, e_range],
                    sample_num=20,
                    timestamp_to_datetime={
                        'lastModifiedDate': 'ms'
                    }
                )
