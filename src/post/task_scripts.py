#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   task_scripts.py
@Author  :   Billy Zhou
@Time    :   2021/09/29
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

import time
import pandas as pd
from typing import List
from src.manager.main import conf  # noqa: E402
from src.post.RequestManager import RequestManager  # noqa: E402
from src.post.multi_requests import multi_requests_by_dicts  # noqa: E402
from src.basic.dataframe_func import records_to_df  # noqa: E402
from src.basic.dataframe_func import df_to_file  # noqa: E402


def change_pools(request_mgr: RequestManager, task_conf: Path, encoding: str = 'utf-8') -> None:
    """change pools according to payload_confs in task_conf"""
    multi_requests_by_dicts(
        request_mgr, conf.read_conf_from_file(task_conf, encoding=encoding)
    )


def mark_id_correct(request_mgr: RequestManager, id_list_conf: Path, task_conf: Path, encoding: str = 'utf-8') -> None:
    """mark the status of id in id_list_conf to correct"""
    id_list_str = conf.read_conf_from_file(id_list_conf, encoding=encoding)
    RWID_dict = {'mark_correct': {'itemSubjectId': id_list_str.split(" ")}}
    log.debug('RWID_dict: {}'.format(RWID_dict))

    result = multi_requests_by_dicts(
        request_mgr,
        tasks_dict=conf.read_conf_from_file(task_conf, encoding=encoding),
        replaces_dict=RWID_dict,
        sleep_time=0.1
    )
    result_false = [{task_name: response} for task_name, responses in result.items() for response in responses if response['code'] != '200']
    log.info(f'false result of mark_id_correct: {result_false}')


def repush_undeleted_ids(request_mgr: RequestManager, task_conf: Path, push_size: int = 500) -> None:
    """repush undelete ids to delete them"""
    tasks_dict = conf.read_conf_from_file(task_conf)
    log.debug(f"tasks_dict: {tasks_dict}")

    # query the undelete ids
    responses_list = multi_requests_by_dicts(request_mgr, tasks_dict)

    res_id_list = []
    for task_name, task_responses in responses_list.items():
        if task_name == 'query_undelete_invaild_RWID':
            for response in task_responses:
                if response['msg'] == '成功':
                    res_id_list.extend(response['data']['records'])
    id_list = [res['id'] for res in res_id_list]
    tot = len(id_list)
    log.debug(f"id_list: {id_list}")
    log.info(f"len of id_list: {tot}")

    if not id_list:
        log.info('No id need to repush')
    else:
        # repush undeleted ids
        log.info(f"time need to repush under push_size[{push_size}]: {(tot-1) // push_size + 1}")
        for i in range((tot - 1) // push_size + 1):
            log.info(f"cur repush time: {i + 1}")
            log.info(f"the slice of id_list[{i}:{i+500}]: {id_list[i:i + 500]}")
            response = request_mgr.send_request(
                'POST',
                request_mgr.read_url('urlgenerateGSCWB'),
                request_payloads=id_list[i:i + 500]
            )
            log.info(f'response: {response}')


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


def query_id_list(
        request_mgr: RequestManager, id_list_conf: Path, id_task_conf: Path,
        query_checkresult: bool = False, query_file_records_of_unvaild_id: bool = False,
        encoding: str = 'utf-8') -> None:
    """read id_list from id_list_conf and query them according to id_task_conf

    Args:
    ----
        request_mgr: RequestManager
            a RequestManager instance
        id_list_conf: Path
            the path of id_list_conf to replace
        id_task_conf: Path
            the path of task_conf for multi_requests_by_dicts
        query_checkresult: bool = False
        query_file_records_of_unvaild_id: bool = False
            the switch whether to output more msg of ids
            when query_checkresult is True, will output the checkresult of ids
            when query_file_records_of_unvaild_id is True, will output the file records of unvaild ids
        encoding: str, default 'utf-8'
            the encode for reading the conf
    """
    # get the list of ids to query
    id_list_str = conf.read_conf_from_file(id_list_conf, encoding=encoding)
    RWID_list = id_list_str.split(" ")
    RWID_dict = {
        'query_id_list': {'id': RWID_list},
        'query_id_checkresult_list': {'itemSubjectId': RWID_list},
    }
    log.debug('RWID_dict: {}'.format(RWID_dict))

    query_id_task = conf.read_conf_from_file(id_task_conf, encoding=encoding)
    log.debug(f"query_id_list: {query_id_task}")
    # not run the task of query_file_of_unvaild_id_list at first
    query_id_task['query_file_of_unvaild_id_list']['task_vaild'] = False
    if not query_checkresult:
        query_id_task['query_id_checkresult_list']['task_vaild'] = False

    # get the responses
    res_id_list = []
    res_id_cr_list = []
    responses_dict = multi_requests_by_dicts(request_mgr, query_id_task, replaces_dict=RWID_dict)
    log.debug('responses_dict: {}'.format(responses_dict))
    for task_name, task_responses in responses_dict.items():
        if task_name == 'query_id_list':
            for response in task_responses:
                if response['msg'] == '成功':
                    res_id_list.extend(response['data']['records'])
        elif task_name == 'query_id_checkresult_list':
            for response in task_responses:
                if response['msg'] == '成功':
                    res_id_cr_list.append(response['data'])
    log.debug('res_id_list: {}'.format(res_id_list))
    log.debug('res_id_cr_list: {}'.format(res_id_cr_list))

    # output to excel file
    RWID_df_filepath = query_id_task['query_id_list']['excel_fpath'].format(
        date=time.strftime("%Y%m%d-%H%M%S", time.localtime())
    ) if not query_checkresult or query_file_records_of_unvaild_id else ''
    RWID_df = records_to_df(
        res_id_list,
        col_list_to_capture=query_id_task['query_id_list']['col_list_to_capture'],
        to_file=RWID_df_filepath
    )

    if query_checkresult:
        # merge two df and output the result
        RWID_checkresult_df = pd.DataFrame.from_records(
            res_id_cr_list
        ).rename(columns={"id": 'unknown_id', 'itemSubjectId': 'id'})
        RWID_records_list_concated = pd.merge(
            RWID_df,
            RWID_checkresult_df[['id', 'remark']],
            on='id'
        )
        df_to_file(
            RWID_records_list_concated,
            to_file=query_id_task['query_id_checkresult_list']['excel_fpath'].format(
                date=time.strftime("%Y%m%d-%H%M%S", time.localtime()))
        )

    # query the records of files which contain the unvaild_id
    if query_file_records_of_unvaild_id:
        for task_name, task_dict in query_id_task.items():
            if task_name != 'query_file_of_unvaild_id_list':
                task_dict['task_vaild'] = False
            else:
                task_dict['task_vaild'] = True

        # get file_unvaild_dict for multi_requests_by_dicts
        unvaild_RWID_df = RWID_df[RWID_df['enableTypeName'] == '失效'].rename(
            columns={"id": 'unvaild_RWID', 'subjectName': 'unvaild_subjectName'})

        if unvaild_RWID_df.empty:
            log.warning('No unvaild id in id_list.')
        else:
            log.info("len of unvaild_RWID_df: {0}".format(len(unvaild_RWID_df)))
            file_unvaild_dict = {'query_file_of_unvaild_id_list': {
                'fileName': list(unvaild_RWID_df['fileName'])}}
            log.info("file_unvaild_dict: {0}".format(file_unvaild_dict))

            responses_dict = multi_requests_by_dicts(
                request_mgr, query_id_task,
                replaces_dict=file_unvaild_dict, encoding=encoding)

            # get responses
            res_file_list = []
            for task_name, task_responses in responses_dict.items():
                for response in task_responses:
                    if task_name == 'query_file_of_unvaild_id_list' and response['msg'] == '成功':
                        res_file_list.extend(response['data']['records'])

            # find the first name in subjectName
            unvaild_RWID_df_subject_firstname = '#' + unvaild_RWID_df['unvaild_subjectName'].str.split(
                '_', expand=True)[0].str.replace(r'[@#]', '', regex=True).rename("subject_firstname")
            unvaild_RWID_df = pd.concat([unvaild_RWID_df, unvaild_RWID_df_subject_firstname], axis=1)
            log.info("unvaild_RWID_df: {}".format(unvaild_RWID_df))

            # get the file_df of unvaild_RWID
            file_df_concated = pd.merge(
                pd.DataFrame.from_records(res_file_list)[['id', 'fileName', 'subjectName', 'enableTypeName']],
                unvaild_RWID_df[['unvaild_RWID', 'unvaild_subjectName', 'fileName', 'subject_firstname']],
                on='fileName'
            )
            df_to_file(
                file_df_concated,
                to_file=query_id_task['query_file_of_unvaild_id_list']['excel_fpath'].format(
                    date=time.strftime("%Y%m%d-%H%M%S", time.localtime()))
            )

            # filter the file_df with subject_firstname and enableTypeName
            file_df_filtered = file_df_concated[
                file_df_concated.apply(lambda x: x.subject_firstname in x.subjectName, axis=1)
            ]
            df_to_file(
                file_df_filtered[file_df_filtered['enableTypeName'] == '有效'],
                to_file=query_id_task['query_file_of_unvaild_id_list']['excel_fpath_filtered'].format(
                    date=time.strftime("%Y%m%d-%H%M%S", time.localtime()))
            )


def requests_to_excel(
        request_mgr: RequestManager, task_conf: Path,
        day_range: List[int] = [], encoding: str = 'utf-8') -> None:
    """post to get responses and output the result to a excel file

    Args:
    ----
        request_mgr: RequestParams
            a RequestParams instance
        task_conf: Path
            the path of conf for multi_requests_increment
        day_range: list, default []
            a list of two int to pass to request_mgr.read_payload

            For example, [-1, 0] meanings the date range between 1 day before and today.
            it will create the output ["2021-08-22T16:00:00.000Z", "2021-08-23T16:00:00.000Z"]
        encoding: str, default 'utf-8'
            the encode for reading the task_conf
    """
    response_list = []
    rq_dicts = conf.read_conf_from_file(task_conf, encoding=encoding)
    log.debug("rq_dicts: {}".format(rq_dicts))

    for task_name, task_dict in rq_dicts.items():
        if not task_dict.get('task_vaild', True):
            if task_dict.get('task_name', ''):
                log.warning('The task[{}] is unvaild. Pass'.format(task_dict['task_name']))
        else:
            log.debug(f"task_dict[{task_name}]: {task_dict}")
            size = int(task_dict.get('size', request_mgr.page_size))
            step = task_dict.get('step', 1)
            max_loop = task_dict.get('max_loop', 10)

            # send first request to get the total
            f_res = request_mgr.send_request(
                "POST",
                request_url=request_mgr.read_url('url'),
                request_payloads=request_mgr.read_payload(task_dict['conf_name'], day_range=day_range)
            )
            response_list.append(f_res)
            log.info("total: %s", f_res['data']['total'])
            log.info("size: %s", size)

            # loop if total bigger than size
            if int(f_res['data']['total']) > int(size):
                looptime = int(f_res['data']['total']) // int(size) + 1
                if looptime > task_dict.get('max_loop', 10):
                    log.warning(f"looptime[{looptime}] over max_loop[{max_loop}]. Truncate it")
                    looptime = f_res
                log.info(f"looptime: {looptime}")

                # get response of the rest
                page_list = [p for p in range(2, looptime + 1, step)]
                log.debug(f'pages_list: {page_list}')
                rest_res_dict = multi_requests_by_dicts(
                    request_mgr, tasks_dict={task_name: task_dict},
                    replaces_dict={task_name: {'current': page_list}},
                    day_range=day_range)
                log.debug(f"len of rest_res[{task_name}]: {len(rest_res_dict[task_name])}")
                log.debug(f"type of rest_res[{task_name}]']: {type(rest_res_dict[task_name])}")
                response_list.extend(rest_res_dict[task_name])

            # capture the records in reponses
            records_list = []
            for response in response_list:
                records_list.extend(response['data']['records'])
            log.debug(f"len of records_list: {len(records_list)}")

            # put records_list into excel
            if records_list:
                records_df = records_to_df(
                    records_list,
                    to_file=task_dict.get('excel_fpath', str(cwdPath.joinpath(
                        task_name + '_{date}.yaml'))).format(
                            date=time.strftime("%Y%m%d-%H%M%S", time.localtime())),
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
            cwdPath.joinpath('res\\dev\\conf\\task\\test_count.yaml')
        )
        log.info(nums_list)

    if False:
        # test requests_to_excel
        requests_to_excel(
            request_mgr,
            cwdPath.joinpath('res\\dev\\conf\\task\\test_excel_uncheck.yaml'), day_range=[-7, -3]
        )

    if False:
        # test query_id_list
        query_id_list(
            request_mgr,
            id_list_conf=cwdPath.joinpath('res\\dev\\test_id_list_query.yaml'),
            id_task_conf=cwdPath.joinpath('res\\dev\\conf\\task\\test_query_id.yaml'),
            query_checkresult=True,
            query_file_records_of_unvaild_id=True
        )

    if True:
        # test repush_undeleted_ids
        repush_undeleted_ids(
            request_mgr,
            cwdPath.joinpath('conf\\task\\repush_undeleted_id.yaml')
        )
