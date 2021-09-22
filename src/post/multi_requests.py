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
from src.manager.main import conf  # noqa: E402


def multi_requests_by_dicts(
        request_mgr: RequestManager,
        requests_dict: Dict[dict, dict] = {
            "your_task_name": {
                'task_vaild': False,
                'task_name': 'your_task_name',
                'no_page': True,
                'request_method': "POST",
                'url_type': 'url',
                'conf_name': 'query\\query_RWID.yaml',
                'replace_word': 'RWID',
            },
        },
        from_file: Path = '',
        from_list: list = [],
        sleep_time: float = 0.3):
    """"""
    if from_file:
        params_list = conf.read_conf_from_file(from_file).split(" ")
        log.debug('params_list: {}'.format(params_list))
        progress_tot = len(params_list)
    elif from_list:
        progress_tot = len(from_list)

    task_no = 0
    task_tot = len(requests_dict)
    responses_dict = {}
    for task_name, rq_args in requests_dict.items():
        task_no += 1
        log.info(f'task progress of multi_requests: {task_no}/{task_tot}')

        responses_dict[task_name] = []
        request_mgr.read_payload(rq_args['conf_name'], no_page=rq_args.get('no_page', True))

        if not from_file and not from_list:
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
            # replace payloads with the params readed from file and send request
            for no, param_to_replace in enumerate(params_list, 1):
                log.info(f'progress of {task_name}: {no}/{progress_tot}')
                try:
                    response = send_request_with_dict(
                        request_mgr, rq_args, replace_word=param_to_replace
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
        max_limit: int = 10, step: int = 1):
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
    request_mgr.read_payload(payload_conf, show_payload=False, day_range=day_range, no_page=False)

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


def send_request_with_dict(
        request_mgr: RequestManager, params: dict = {
            'task_vaild': True,
            'task_name': '',
            'request_method': "POST",
            'url_type': 'url',
            'conf_name': 'query\\query_RWID.yaml',
            'replace_word': 'RWID',
        }, replace_word: str = ''):
    """send a request using params in a dict"""
    if not params.get('task_vaild', True):
        if params.get('task_name', ''):
            log.warning('The task[{}] is unvaild. Pass'.format(params['task_name']))
    else:
        if params['request_method'].upper() == 'GET':
            return request_mgr.send_request(
                "GET",
                url=request_mgr.read_url(params['url_type']),
                url_type=params['url_type'],
                task_name=params.get('task_name', '')
            )
        else:
            if replace_word and params.get('replace_word'):
                payloads = request_mgr.payloads[
                    params['conf_name']].replace(
                    params['replace_word'], replace_word)
            else:
                payloads = request_mgr.payloads[params['conf_name']]
            return request_mgr.send_request(
                "POST",
                url=request_mgr.read_url(params['url_type']),
                request_payloads=payloads,
                url_type=params['url_type'],
                task_name=params.get('task_name', '')
            )


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

    if False:
        # test multi_requests
        filepath = cwdPath.joinpath('res\\pro\\id_list.yaml')
        mark_correct = conf.read_conf_from_file(cwdPath.joinpath('conf\\task\\mark_correct.yaml'))
        log.debug(f"mark_correct: {mark_correct}")
        responses_dict = multi_requests_by_dicts(request_mgr, mark_correct, from_file=filepath)
        log.info('responses_dict: {}'.format(responses_dict))
