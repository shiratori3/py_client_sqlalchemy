#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   RequestParams.py
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

import json
import time
import datetime
import requests
from functools import wraps
from src.manager.main import conf  # noqa: E402


def send_request_with_dict(func):
    """A decorator to send a request using params in a dict"""
    @wraps(func)
    def wrapper(*args, task_dict: dict = {}, **kwargs):
        if not task_dict:
            return func(*args, **kwargs)
        else:
            try:
                # check the vaild of request_method
                if task_dict['request_method'].upper() not in ['POST', 'GET']:
                    raise ValueError('Invaild request_method[{}] in task_dict[{}].'.format(
                        task_dict['request_method'], task_dict))

                if task_dict['request_method'].upper() == 'GET':
                    return func(
                        *args, request_method=task_dict['request_method'],
                        request_url=task_dict['request_url'],
                        request_payloads=task_dict.get('request_payloads', ''),
                        url_type=task_dict['url_type'],
                        task_name=task_dict.get('task_name', ''), **kwargs)
                else:
                    return func(
                        *args, request_method=task_dict['request_method'],
                        request_url=task_dict['request_url'],
                        request_payloads=task_dict.get('request_payloads', ''),
                        url_type=task_dict['url_type'],
                        task_name=task_dict.get('task_name', ''),
                        payloads_encode=task_dict.get('payloads_encode', ''), **kwargs)
            except Exception as e:
                log.error('An error occurred. {!r}'.format(e.args))
                log.error(f'Failed to send request with a task_dict. The task_dict is: \n{task_dict}')
    return wrapper


def request_task_msgs(func):
    """A decorator to output additional msgs of request tasks"""
    @wraps(func)
    def wrapper(self, *args, url_type: str = '', task_name: str = '', **kwargs):
        response = func(self, *args, **kwargs)
        if response and isinstance(response, dict) and task_name:
            if url_type == 'urlChange':
                log.info(f"{task_name} 切换成功")
            elif url_type == 'urlgetSql':
                log.info(f"{task_name} 执行成功")
                log.info("{} 总量: {}".format(task_name, response['data']['count']))
                log.info("{} 涉及公告数: {}".format(task_name, response['data']['influenceItemCount']))
                log.info("{} 涉及科目数: {}".format(task_name, response['data']['influenceSubjectCount']))
        return response
    return wrapper


class RequestManager(object):
    """Manage the urls, headers and payloads to create and send requests

    Attrs:
    -----
        conf_path: Path, default cwdPath.joinpath('conf')
            the directory of conf file
        _conf_file: Path, default cwdPath.joinpath('conf').joinpath(conf_fname)
            the path of conf file
        page_size: int
            the num of conf_dict['page']['size'] readed from _conf_file
        url_dict: dict
            conf_dict['url'] readed from _conf_file
        headers: dict
            conf_dict['headers'] read from _conf_file
            updated with conf_dict['cookie']['gsid'] and conf_dict['cookie']['token']
        payloads: dict
            the dict saving payload_dict readed from conf_path.joinpath(conf_fpath)

    Methods:
    -------
        read_conf(
                self, conf_fname: str,
                conf_path: Path = cwdPath.joinpath('conf'), encoding: str = ''
            ) -> None:
            read from conf_path.joinpath(conf_fname) to update self.url_dict, self.headers, self.page_size
        read_url(self, url_type: str, **params) -> str:
            read url in self.url_dict and format with timestamp
        read_payload(
                self, conf_fpath: str,
                base_path: Path = '', encoding: str = '', day_range: list = []
            ) -> dict:
            read payload from base_path.joinpath(conf_fpath) and update params in payload
        send_request(
                self, request_method: str, request_url: str,
                request_headers: str = '', request_payloads: dict = {},
                json_encoding: str = ''
            ) -> dict or requests.Response:
            send a request and return response
    """
    def __init__(self, conf_path: Path = cwdPath.joinpath('conf')):
        self.conf_path = conf_path

        self.url_dict = {}
        self.headers = {}
        self.payloads = {}

    def read_conf(self, conf_fname: str, conf_path: Path = cwdPath.joinpath('conf'), encoding: str = '') -> None:
        """read from conf_path.joinpath(conf_fname) to update self.url_dict, self.headers, self.page_size"""

        self._conf_file = Path(conf_path).joinpath(conf_fname)
        conf_dict = conf.read_conf_from_file(self._conf_file, encoding=encoding)
        log.debug(f"conf_dict: \n{conf_dict}")

        # update url_dict
        self.url_dict = conf_dict['url']

        # update size
        self.page_size = int(conf_dict['page']['size'])

        # update headers
        conf_dict['headers']['gsid'] = conf_dict['cookie']['gsid']
        conf_dict['headers']['Authorization'] = 'Bearer ' + conf_dict['cookie']['token']
        self.headers = conf_dict['headers']

    def read_url(self, url_type: str, **params) -> str:
        """read url in self.url_dict and format with timestamp and **params"""
        log.debug(f'url_dict: {self.url_dict}')
        if self.url_dict.get(url_type):
            return self.url_dict[url_type].format(timestamp=int(round(time.time() * 1000)), **params)
        else:
            log.error("Unvaild url_type. Return blank string.")
            return ''

    def read_payload(
            self, conf_fpath: str, day_range: list = [],
            base_path: Path = '', encoding: str = '', use_history: bool = True) -> dict:
        """read payload from base_path.joinpath(conf_fpath) and update params in payload

        Args:
        ----
            conf_fpath: str
                the relative filepath of payload conf file to read
            day_range: list, default []
                a list of two int to update the 'lastModifiedDateRange' param in payload

                For example, [-1, 0] meanings the date range between 1 day before and today.
                it will create the output ["2021-08-22T16:00:00.000Z", "2021-08-23T16:00:00.000Z"]
            base_path: Path = ''
                the base directory to read conf file, if unprovide, use self.base_path
            encoding: str, default ''
                the encode for reading the conffile
            use_history: bool, default True
                if conf_fpath in self.payloads, return self.payloads[conf_fpath] when True
        Return:
            self.conf_dict['payload']: dict
        """
        if self.payloads.get(conf_fpath) and use_history:
            log.warning(f'{conf_fpath} already readed. Use the one in payloads')
            return self.payloads[conf_fpath]
        else:
            base_path = Path(base_path) if base_path else self.conf_path
            conf_dict = conf.read_conf_from_file(
                base_path.joinpath(conf_fpath), encoding=encoding)
            log.debug(f'conf_dict readed: {conf_dict}')

            # change params in conf_dict
            self._update_payload_params(
                conf_dict['payload'], page_size=self.page_size, day_range=day_range)
            log.debug(f'conf_dict updated: {conf_dict}')

            # add to self.payloads
            self.payloads[conf_fpath] = conf_dict['payload']
            return conf_dict['payload']

    def _update_payload_params(self, payload: dict, page_size: int = '', day_range: list = []) -> None:
        """update the params in payload"""
        # change page size in conf_dict
        if payload.get('page', None) is not None:
            if page_size:
                if isinstance(payload['page'].get('size', None), int):
                    if page_size > payload['page']['size']:
                        payload['page']['size'] = page_size
        # change lastModifiedDateRange in conf_dict
        if payload.get('lastModifiedDateRange', None) is not None:
            if day_range:
                log.debug("datetime.datetime.utcnow(): %s", datetime.datetime.utcnow())
                utc_now = datetime.datetime.utcnow()
                if len(day_range) == 1:
                    s_delta = datetime.timedelta(days=day_range[0] - 1)
                    e_delta = datetime.timedelta(days=-1)
                else:
                    if len(day_range) > 2:
                        log.warning('Too many arguments for day_range. Only available for the first two')
                    s_delta = datetime.timedelta(days=day_range[0] - 1)
                    e_delta = datetime.timedelta(days=day_range[1] - 1)
                s_date = utc_now + s_delta
                e_date = utc_now + e_delta
                log.debug("s_date: %s", s_date.strftime('%Y-%m-%d') + 'T16:00:00.000Z')
                log.debug("e_date: %s", e_date.strftime('%Y-%m-%d') + 'T16:00:00.000Z')
                payload['lastModifiedDateRange'] = [
                    s_date.strftime('%Y-%m-%d') + 'T16:00:00.000Z',
                    e_date.strftime('%Y-%m-%d') + 'T16:00:00.000Z',
                ]
                log.info("lastModifiedDateRange: %s", payload['lastModifiedDateRange'])

    @send_request_with_dict
    @request_task_msgs
    def send_request(
            self, request_method: str, request_url: str,
            request_headers: str = '', request_payloads: dict = {},
            payloads_encode: str = '') -> dict or requests.Response:
        """send a request and return response

        send a request and return response.
        if response code not equal to 200, output the info of params for debug.

        Args:
            request_method: str
                the method to send request, must in ['POST', 'GET']
            request_url: str
                the url to send a request and get response
            request_headers: str, default ''
            request_payloads: dict, default {}
                the payload and header used to create request instead of those in RequestParams

        Returns:
            a dict of json type. if response.json() failed, requests.Response
        """
        if request_method.upper() not in ['POST', 'GET']:
            raise ValueError(f'Invaild request_method[{request_method}]. Please input POST or GET.')

        headers = request_headers if request_headers else self.headers
        if request_payloads:
            payloads = json.dumps(request_payloads) if not payloads_encode else json.dumps(
                request_payloads).encode(payloads_encode)
            response = requests.request(
                request_method,
                url=request_url,
                headers=headers,
                data=payloads
            )
        else:
            response = requests.request(
                request_method,
                url=request_url,
                headers=headers
            )

        log.debug("response.text: %s", response.text)
        try:
            response_jsondict = response.json()
            log.debug("response_msg: %s", response_jsondict['msg'])
            if response_jsondict['code'] != 200:
                log.error("request failed.")
                log.warning(f"request_method: {request_method}")
                log.warning(f"url: {request_url}")
                log.warning(f"headers: {headers}")
                log.warning(f"payload: {payloads}")
                log.warning(f"response.text[:1000]: {response.text[:1000]}")
            else:
                return response_jsondict
        except Exception:
            log.error('The response body does not contain valid json. Returning requests.Response')
            log.error(f"request_method: {request_method}")
            log.error(f"url: {request_url}")
            log.error(f"headers: {headers}")
            log.error(f"payload: {payloads}")
            log.error(f"response.text[:1000]: {response.text[:1000]}")
            return response


if __name__ == '__main__':
    request_mgr = RequestManager()
    request_mgr.read_conf('settings.yaml')

    if False:
        # test headers and url_dict
        log.info(f"headers: {request_mgr.headers}")
        log.info(f"url of urlgetSql: {request_mgr.read_url('urlgetSql')}")

    if True:
        # test payload
        payload1 = request_mgr.read_payload('post\\excel\\excel_uncheck.yaml')
        payload2 = request_mgr.read_payload('post\\excel\\excel_check_tan_latest.yaml', day_range=[-1, 0])
        payload3 = request_mgr.read_payload('post\\poolchange\\poolchange_juno_error_inner.yaml')
        log.info(f"payload1: \n{json.dumps(payload1)}")
        log.info(f"payloads: \n{request_mgr.payloads}")

    if True:
        # test send_request
        response = request_mgr.send_request(
            "POST",
            request_url=request_mgr.read_url('url'),
            request_payloads=payload1
        )
        if response.get('code', None) is not None:
            log.info(f"code of response: {response['code']}")
            log.info(f"msg of response: {response['msg']}")
            if response.get('data', None) is not None:
                if response.get('total', None) is not None:
                    log.info(f"total of response: {response['data']['total']}")
        else:
            log.error('Failure request')
