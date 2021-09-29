#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   multi_requests.py
@Author  :   Billy Zhou
@Time    :   2021/09/29
@Desc    :   None
'''


import sys
from pathlib import Path

cwdPath = Path(__file__).parents[2]  # the num depend on your filepath
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr
log = logmgr.get_logger(__name__)

import time
from typing import List, Dict, Any, Mapping
from collections import defaultdict
from src.post.RequestManager import RequestManager  # noqa: E402
from src.manager.main import conf  # noqa: E402


def multi_requests_by_dicts(
        request_mgr: RequestManager,
        tasks_dict: Dict[str, dict] = {}, replaces_dict: Dict[str, Dict[str, list]] = {}, day_range: list = [],
        sleep_time: float = 0.3, encoding: str = '') -> Dict[str, List[dict]]:
    """send multi requests according to task_dicts

    Args:
    ----
        request_mgr: RequestManager
        tasks_dict: Dict[str, dict] = {}
            the dict of params to send requests
            for example:
                tasks_dict = {
                    "task1_name": {
                        'task_vaild': False,
                        'request_method': "POST",
                        'url_type': 'url',
                        'conf_name': 'query\\query_RWID.yaml',
                        'payloads_encode': 'utf-8',
                        'base_to_replace': {'payload': {'id': 'RWID'}},
                    }
                }
            for more detail, to see the sample file under ./res/dev/task_sample.yaml
        replaces_dict: Dict[str, Dict[str, list]] = {}
            the dict of values to replace params in payload or url
            for example:
                replaces_dict = {
                    'your_task_name': {'key_of_value_to_replace': value_list_to_replace}},
                    'task1':  {'id': []},
                    'task2': {'itemSubjectId': []},
                }
        sleep_time: float = 0.3
            time to sleep after each request
        encoding: str = ''
            the encode type for request_mgr.read_payload(encoding=encoding)

    Returns:
    -------
        responses_dict: Dict[str, List[Dict]]
            a dict of lists of response_dict from diff tasks
            for example:
                responses_dict = {
                    'task1': [response1, response2],
                    'task2': [response3, response4],
                }
    """
    task_no = 0
    task_tot = len(tasks_dict)
    responses_dict = defaultdict(list)
    for task_name, task_dict in tasks_dict.items():
        task_no += 1
        log.info(f'task progress of multi_requests: {task_no}/{task_tot}')
        if task_dict.get('task_vaild', None) is None:
            log.error('The task[{}] don\'t have the task_vaild attr. Pass'.format(
                task_dict.get('task_name', 'Unknown')))
        elif not task_dict.get('task_vaild', None):
            log.warning('The task[{}] is unvaild. Pass'.format(
                task_dict.get('task_name', 'Unknown')))
        else:
            # read the payload from task_dict['conf_name']
            if task_dict.get('conf_name'):
                payload = request_mgr.read_payload(
                    task_dict['conf_name'],
                    encoding=encoding, day_range=day_range)

            if not replaces_dict or not replaces_dict.get(task_name):
                # send the request with task_dict params
                try:
                    task_dict['request_url'] = request_mgr.read_url(task_dict.get('url_type'))
                    task_dict['request_payloads'] = request_mgr.payloads[task_dict.get('conf_name')]
                    response = request_mgr.send_request(task_dict=task_dict)
                    if response:
                        log.debug(f"response: \n{response}")
                        responses_dict[task_name].append(response)
                except Exception as e:
                    log.error('An error occurred. {}'.format(e.args[-1]))
                finally:
                    time.sleep(sleep_time)
            elif not task_dict.get('base_to_replace'):
                log.error(f'No base_to_replace in task_dict[{task_dict}]')
            else:
                # send the request with replaced params
                log.debug(f'replaces_dict[{task_name}]: {replaces_dict[task_name]}')
                log.debug(f"task_dict['base_to_replace']: {task_dict['base_to_replace']}")

                for v_list in replaces_dict[task_name].values():
                    # get the list of key_list in task_dict['base_to_replace']
                    k_lists = generate_key_lists_of_base(task_dict['base_to_replace'])
                    log.debug(f'k_lists: {k_lists}')

                    log.debug(f'v_list: {v_list}')
                    progress_tot = len(v_list)
                    for no, v in enumerate(v_list, 1):
                        log.info(f'progress of {task_name}: {no}/{progress_tot}')
                        log.debug(f'value_for_replace: {v}')

                        # generate replaced payload or url
                        if k_lists[0][0] == 'payload':
                            task_dict['request_payloads'] = set_value_of_dict_by_key_list(
                                v, payload, k_lists[0][1:])
                            log.debug(f"payload_replaced: {task_dict['request_payloads']}")
                        elif k_lists[0][0] == 'url':
                            url_params = set_value_of_dict_by_key_list(
                                v, task_dict['base_to_replace']['url'], k_lists[0][1:])
                            log.debug(f'url_params: {url_params}')
                            task_dict['request_url'] = request_mgr.read_url(
                                task_dict['url_type'], **url_params)
                            log.debug(f"url[{task_dict['url_type']}]_replaced: {task_dict['request_url']}")

                        # use the default if no replaced url
                        if not task_dict.get('request_url'):
                            task_dict['request_url'] = request_mgr.read_url(task_dict.get('url_type'))

                        try:
                            log.debug(f"task_dict: \n{task_dict}")
                            response = request_mgr.send_request(task_dict=task_dict)
                            if response:
                                log.debug(f"response: \n{response}")
                                responses_dict[task_name].append(response)
                        except Exception as e:
                            log.error('An error occurred. {}'.format(e.args[-1]))
                        finally:
                            time.sleep(sleep_time)

    return responses_dict


def generate_key_lists_of_base(base_dict: dict) -> List[list]:
    """return the list of key_list of base_dict"""
    key_lists = []
    for key in base_dict.keys():
        key_list = [key]
        next = base_dict[key]
        while next and isinstance(next, Mapping):
            for k, v in next.items():
                next = v
                key_list.append(k)
        key_lists.append(key_list)
    log.debug(f"key_lists: {key_lists}")
    return key_lists


def set_value_of_dict_by_key_list(v_to_replace: Any, dict_to_set: dict, k_list: list) -> dict:
    "set the value in dict_to_set according ot k_list and return replaced dict_to_set"
    log.debug(f'dict_to_set: {dict_to_set}')
    log.debug(f'k_list: {k_list}')
    log.debug(f'v: {v_to_replace}')

    len_k = len(k_list)
    d = dict_to_set
    sub = ''
    for no, k in enumerate(k_list, 1):
        sub += '[' + k_list[no - 1] + ']'
        log.debug(f'sub: {sub}')
        if no != len_k:
            if d.get(k, None) is None:
                raise KeyError(f'Unfound key{sub} of k_list[{k_list}] in dict[{dict_to_set}]')
            else:
                log.debug(f'key: {k}')
                log.debug(f'dict[key]: {d[k]}')
                d = d[k]
        else:
            d[k] = v_to_replace
            log.debug(f'replaced dict_to_set: {dict_to_set}')
            return dict_to_set


if __name__ == '__main__':
    request_mgr = RequestManager()
    request_mgr.read_conf('settings.yaml')

    if False:
        # test generate_key_list_of_base
        base_dict = {
            'payload': {'id': 'RWID'},
            "url": {'urlCheckResult': {'itemSubjectId': 'RWID'}},
        }
        k_lists = generate_key_lists_of_base(base_dict)
        log.info(f'k_lists: {k_lists}')

    if False:
        # test set_value_of_dict_by_key_list
        RWID_list_str = conf.read_conf_from_file(
            cwdPath.joinpath('res\\dev\\test_id_list_query.yaml'))
        RWID_dict = {
            'query_id_list': {'id': RWID_list_str.split(" ")},
        }
        log.info(f"RWID_dict: {RWID_dict}")

        query_id_task = conf.read_conf_from_file(
            cwdPath.joinpath('res\\dev\\conf\\task\\test_query_id.yaml'), encoding='utf-8')
        query_id_task['query_id_checkresult_list']['task_vaild'] = False
        query_id_task['query_file_of_unvaild_id_list']['task_vaild'] = False

        for task_name, task_dict in query_id_task.items():
            if task_dict.get('conf_name'):
                payload = request_mgr.read_payload(task_dict['conf_name'], encoding='utf-8')
                log.debug(f'payload: {payload}')
            if task_dict.get('base_to_replace'):
                k_lists = generate_key_lists_of_base(task_dict['base_to_replace'])
                if k_lists and RWID_dict.get(task_name):
                    log.debug(f'RWID_dict[{task_name}]: {RWID_dict[task_name]}')
                    for v_list in RWID_dict[task_name].values():
                        for v in v_list:
                            log.debug(f'value_for_replace: {v}')
                            if k_lists[0][0] == 'payload':
                                payload_replaced = set_value_of_dict_by_key_list(v, payload, k_lists[0][1:])
                                log.info(f'payload_replaced: {payload_replaced}')

    if True:
        # test multi_requests
        if False:
            # read tasks_dict
            mark_correct = conf.read_conf_from_file(
                cwdPath.joinpath('res\\dev\\conf\\task\\test_mark_correct.yaml'))
            log.debug(f"mark_correct: {mark_correct}")

            # read id_list
            RWID_list_str = conf.read_conf_from_file(
                cwdPath.joinpath('res\\dev\\test_id_list_mark.yaml'))
            RWID_dict = {
                'mark_correct': {'id': RWID_list_str.split(" ")},
            }
            log.info(f"RWID_dict: {RWID_dict}")

            responses_dict = multi_requests_by_dicts(
                request_mgr,
                mark_correct,
                replaces_dict=RWID_dict
            )
            log.info('responses_dict: {}'.format(responses_dict))

        if True:
            # read tasks_dict
            query_id_task = conf.read_conf_from_file(
                cwdPath.joinpath('res\\dev\\conf\\task\\test_query_id.yaml'), encoding='utf-8')
            query_id_task['query_id_checkresult_list']['task_vaild'] = True
            query_id_task['query_file_of_unvaild_id_list']['task_vaild'] = False
            log.debug(f"query_id_list: {query_id_task}")

            # read id_list
            RWID_list_str = conf.read_conf_from_file(
                cwdPath.joinpath('res\\dev\\test_id_list_query.yaml'))
            RWID_dict = {
                'query_id_list': {'id': RWID_list_str.split(" ")},
                'query_id_checkresult_list': {'itemSubjectId': RWID_list_str.split(" ")},
            }
            log.info(f"RWID_dict: {RWID_dict}")

            res_id_list = []
            res_id_check_list = []

            responses_dict = multi_requests_by_dicts(
                request_mgr, query_id_task, replaces_dict=RWID_dict, encoding='utf-8')
            log.debug('responses_dict: {}'.format(responses_dict))
            for task_name, task_responses in responses_dict.items():
                for response in task_responses:
                    if task_name == 'query_id_list' and response['msg'] == '成功':
                        res_id_list.append(response['data']['records'])
                    elif task_name == 'query_id_checkresult_list' and response['msg'] == '成功':
                        res_id_check_list.append(response['data'])
            log.info(res_id_check_list)
