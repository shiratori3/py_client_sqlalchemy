#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   multi_requests.py
@Author  :   Billy Zhou
@Time    :   2021/09/22
@Desc    :   None
'''


import sys
from pathlib import Path

cwdPath = Path(__file__).parents[2]  # the num depend on your filepath
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr
log = logmgr.get_logger(__name__)

import time
from typing import Dict
from src.post.RequestManager import RequestManager  # noqa: E402
from src.post.RequestManager import send_request_with_dict  # noqa: E402
from src.manager.main import conf  # noqa: E402


def multi_requests_by_dicts(
        request_mgr: RequestManager,
        requests_dict: Dict[str, dict] = {
            "your_task_name": {
                'task_vaild': False,
                'task_name': 'your_task_name',
                'request_method': "POST",
                'url_type': 'url',
                'conf_name': 'query\\query_RWID.yaml',
                'encode': 'utf-8',
                'replace_old_dict': {'RWID': 'RWID'},
            },
        },
        replace_new_dict: Dict[str, list] = {},
        sleep_time: float = 0.3,
        read_encoding: str = '') -> dict:
    """"""
    task_no = 0
    task_tot = len(requests_dict)
    responses_dict = {}
    for task_name, rq_args in requests_dict.items():
        task_no += 1
        log.info(f'task progress of multi_requests: {task_no}/{task_tot}')
        if not rq_args.get('task_vaild', True):
            log.warning('The task[{}] is unvaild. Pass'.format(rq_args.get('task_name', 'Unknown')))
        else:
            responses_dict[task_name] = []
            if rq_args.get('conf_name'):
                if read_encoding:
                    request_mgr.read_payload(
                        rq_args['conf_name'],
                        read_encoding=read_encoding)
                else:
                    request_mgr.read_payload(rq_args['conf_name'])

            if not requests_dict[task_name].get('replace_old_dict'):
                # no replace to send request
                try:
                    response = send_request_with_dict(request_mgr, rq_args)
                    if response:
                        log.debug(f"response: \n{response}")
                        responses_dict[task_name].append(response)
                except Exception as e:
                    log.error('An error occurred. {}'.format(e.args[-1]))
                finally:
                    time.sleep(sleep_time)
            else:
                # check the vaild of replace_new_dict
                if not replace_new_dict:
                    log.error('Empty replace_new_dict while replace_old_dict is not empty')
                else:
                    invaild_new_key = []
                    for key in replace_new_dict.keys():
                        if not requests_dict[task_name]['replace_old_dict'].get(key):
                            invaild_new_key.append(key)
                            log.error("Invaild key[{}] in replace_new_dict to \
                                replace with replace_old_dict[{}]".format(
                                key, requests_dict[task_name]['replace_old_dict']
                            ))
                    for drop_key in invaild_new_key:
                        replace_new_dict.pop(drop_key)
                    # send the request with replaced params
                    for key, news in replace_new_dict.items():
                        progress_tot = len(news)
                        # replace payloads with the params readed from file and send request
                        for no, new in enumerate(news, 1):
                            log.info(f'progress of {task_name}: {no}/{progress_tot}')
                            try:
                                response = send_request_with_dict(
                                    request_mgr, rq_args, replace_new_dict={key: new}
                                )
                                if response:
                                    log.debug(f"response: \n{response}")
                                    responses_dict[task_name].append(response)
                            except Exception as e:
                                log.error('An error occurred. {}'.format(e.args[-1]))
                            finally:
                                time.sleep(sleep_time)

    return responses_dict


def multi_requests_increment(
        request_mgr: RequestManager, payload_conf: str,
        day_range: list = [],
        max_limit: int = 10, step: int = 1) -> list:
    """get mutli responses, combine their responses and

    Args:
    ----
        request_mgr: RequestManager
            a RequestManager instance
        payload_conf: str
            the name of payload_conf_fname to read from RequestManager
        day_range: list, default []
            a list of two datetime str to pass to request_mgr.read_payload

            For example, ["2021-08-22T00:00:00.000Z", "2021-08-23T00:00:00.000Z"]
        max_limit: int, default 10
            the maximum limit of increment
        step: int, default 1
            the step of increment

    Return:
    ------
        records_list: list
            a list of response dicts
    """
    request_mgr.read_payload(payload_conf, show_payload=False, day_range=day_range)

    response_dict = request_mgr.send_request(
        "POST", url=request_mgr.read_url('url'),
        request_payloads=request_mgr.payloads[payload_conf]
    )
    if response_dict and isinstance(response_dict, dict):
        records_list = response_dict['data']['records']

        # loop if total bigger than size
        log.info("total: %s", response_dict['data']['total'])
        log.info("size: %s", response_dict['data']['size'])
        if int(response_dict['data']['total']) > int(response_dict['data']['size']):
            looptime = int(response_dict['data']['total']) // int(response_dict['data']['size']) + 1
            if looptime > max_limit:
                looptime = max_limit
            log.info("looptime: %s", looptime)
            for _ in range(1, looptime):
                # update page param in payload
                request_mgr.update_payload_page(payload_conf, step=step)
                response_dict_looped = request_mgr.send_request(
                    "POST",
                    url=request_mgr.read_url('url'),
                    request_payloads=request_mgr.payloads[payload_conf]
                )
                if response_dict_looped and isinstance(response_dict_looped, dict):
                    records_list.extend(response_dict_looped['data']['records'])

        return records_list


if __name__ == '__main__':
    request_mgr = RequestManager()
    request_mgr.read_conf('settings.yaml')

    if False:
        # test send_request_with_dict
        count_uncheck = conf.read_conf_from_file(cwdPath.joinpath(cwdPath.joinpath('conf\\task\\count_uncheck_tan.yaml')))
        log.info(f"count_uncheck: {count_uncheck}")
        responses_dict = multi_requests_by_dicts(request_mgr, count_uncheck)

        num_list = []
        for task_name, records_list in responses_dict.items():
            log.debug("length of responses_dict.value: {}".format(len(records_list)))
            res = records_list[0]
            if res['msg'] == '成功':
                log.debug("keys of responses_dict.value[0]: {}".format(res.keys()))
                num_list.append(
                    int(res['data']['total']))
        log.info(num_list)

    if True:
        # test multi_requests
        RWID_list_str = conf.read_conf_from_file(cwdPath.joinpath('res\\pro\\id_list.yaml'))
        RWID_dict = {'payload': {'RWID': RWID_list_str.split(" ")}}
        log.debug(f"RWID_dict: {RWID_dict}")

        if False:
            mark_correct = conf.read_conf_from_file(cwdPath.joinpath('conf\\task\\mark_correct.yaml'))
            log.debug(f"mark_correct: {mark_correct}")
            responses_dict = multi_requests_by_dicts(request_mgr, mark_correct, replace_new_dict=RWID_dict)
            log.info('responses_dict: {}'.format(responses_dict))

        if True:
            responses_data_id_list = []
            responses_data_id_checkresult_list = []
            query_id_list = conf.read_conf_from_file(cwdPath.joinpath('conf\\task\\query_id_list.yaml'))
            log.debug(f"query_id_list: {query_id_list}")

            responses_dict = multi_requests_by_dicts(request_mgr, query_id_list, replace_new_dict=RWID_dict)
            log.debug('responses_dict: {}'.format(responses_dict))
            for task_name, task_responses in responses_dict.items():
                for response in task_responses:
                    if task_name == 'query_id_list' and response['msg'] == '成功':
                        responses_data_id_list.append(response['data']['records'])
                    elif task_name == 'query_id_checkresult_list' and response['msg'] == '成功':
                        responses_data_id_checkresult_list.append(response['data'])
            print(responses_data_id_checkresult_list)
