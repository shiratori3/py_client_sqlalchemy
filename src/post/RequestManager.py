#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   RequestParams.py
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

import json
import time
import inspect
import datetime
import requests
from typing import Dict, Any
from src.manager.main import conf  # noqa: E402
from functools import wraps
from src.basic.compare import dict_compare  # noqa: E402
from src.post.task_msgs import request_task_msgs  # noqa: E402


def send_request_with_dict(func):
    """A decorator to send a request using params in a dict"""
    @wraps(func)
    def wrapper(self, *args, params_dict: dict = {}, replace_new_dict: Dict[str, Any] = {}, **kwargs):
        if not params_dict:
            return func(*args, **kwargs)
        else:
            if not params_dict.get('task_vaild', True):
                log.warning('The task[{}] is unvaild. Pass'.format(params_dict.get('task_name', '')))
            else:
                # check the vaild of request_method
                if params_dict['request_method'].upper() not in ['POST', 'GET']:
                    raise ValueError('Invaild request_method[{}] in task[].'.format(
                        params_dict['request_method']))

                # check the vaild of replace_new_dict
                if replace_new_dict and params_dict.get('replace_old_dict'):
                    old_compared = dict_compare(
                        params_dict['replace_old_dict'], replace_new_dict,
                        miss_checkmode='ADD', diff_checkmode='IGNORE')
                    if old_compared != params_dict['replace_old_dict']:
                        for key in old_compared.keys():
                            if not params_dict['replace_old_dict'].get(key):
                                invaild_new_key.append(key)
                                log.error("Invaild key[{}] in replace_new_dict to \
                                    replace with replace_old_dict[{}]".format(
                                    key, params_dict['replace_old_dict']
                                ))
                    invaild_new_key = []
                    for key in replace_new_dict.keys():
                    for drop_key in invaild_new_key:
                        replace_new_dict.pop(drop_key)

                # use the params with params_dict
                url = request_mgr.read_url(params_dict['url_type'])
                payloads = request_mgr.payloads[params_dict['conf_name']]
                # replace the params with replace_new_dict
                if params_dict['request_method'].upper() == 'GET':
                    if replace_new_dict and params_dict.get('replace_old_dict'):
                        url = request_mgr.read_url(
                            params_dict['url_type'], **replace_new_dict)
                else:
                    if replace_new_dict and params_dict.get('replace_old_dict'):
                        for key, new in replace_new_dict.items():
                            payloads = payloads.replace(
                                params_dict['replace_old_dict'][key], new)
                    if params_dict.get('payloads_encode'):
                        payloads = payloads.encode(params_dict['payloads_encode'])
            return func(
                *args, request_method=params_dict['request_method'],
                url=url,
                request_payloads=payloads,
                url_type=params_dict['url_type'],
                task_name=params_dict.get('task_name', ''))
    return wrapper


class RequestManager(object):
    """Manage the urls, headers and payloads to create and send requests

    Attrs:
    -----
        conf_path: Path, default cwdPath.joinpath('conf/post')
            the directory of conf files
        conf_fname: str
            the filename of conf file
        url_dict: dict
            conf_dict['url'] readed from conf_path.joinpath(conf_fname)
        headers: dict
            conf_dict['headers'] read from conf_path.joinpath(conf_fname)
            updated with conf_dict['cookie']['gsid'] and conf_dict['cookie']['token']
        payloads: dict
            the dict saving payload_dict readed from conf_path.joinpath(payload_conf_fname)

    Methods:
    -------
        read_conf(self, conf_fname: str) -> None:
            read from conf_path.joinpath(conf_fname) and update headers
        read_url(self, url_type: str, **params) -> str:
            read url in self.url_dict and format with timestamp
        read_payload(
                self, payload_conf_fname: str,
                show_payload: bool = False, day_range: list = []
            ) -> dict:
            read payload from conf_path.joinpath(payload_conf_fname) and update params in payload
        send_request(
                self, request_method: str, url: str,
                request_payloads: str = '', request_headers: str = ''
            ) -> dict or requests.Response:
            send a request and return response
    """
    def __init__(self, conf_path: Path = cwdPath.joinpath('conf/post')):
        self.conf_path = Path(conf_path)

        self.url_dict = {}
        self.headers = {}
        self.payloads = {}

    def read_conf(self, conf_fname: str) -> None:
        """read from conf_path.joinpath(conf_fname) and update headers"""
        conf_dict = conf.read_conf_from_file(self.conf_path.joinpath(conf_fname))
        log.debug("conf_dict: %s", conf_dict)

        # update url_dict
        self.url_dict = conf_dict['url']

        # update size
        self.page_size = conf_dict['page']['size']

        # update headers
        conf_dict['headers']['gsid'] = conf_dict['cookie']['gsid']
        conf_dict['headers']['Authorization'] = 'Bearer ' + conf_dict['cookie']['token']
        self.headers = conf_dict['headers']

    def read_url(self, url_type: str, **params) -> str:
        """read url in self.url_dict and format with timestamp"""
        log.debug(f'url_dict: {self.url_dict}')
        if self.url_dict.get(url_type):
            return self.url_dict[url_type].format(timestamp=int(round(time.time() * 1000)), **params)
        else:
            log.error("Unvaild url_type. Return blank url.")
            return ''

    def read_payload(
            self, payload_conf_fname: str,
            show_payload: bool = False, read_encoding: str = '',
            day_range: list = []) -> None:
        """read payload from conf_path.joinpath(payload_conf_fname) and update params in payload

        Args:
            payload_conf_fname: str
                the filename of payload conf to read
            show_payload: bool, default False
                show payload readed for debug
            day_range: list, default []
                a list of two datetime str to update the 'lastModifiedDateRange' param in payload

                For example, ["2021-08-22T00:00:00.000Z", "2021-08-23T00:00:00.000Z"]
        """
        if self.payloads.get(payload_conf_fname):
            return self.payloads[payload_conf_fname]
        else:
            if read_encoding:
                self._payload_conf_dict = conf.read_conf_from_file(
                    self.conf_path.joinpath(payload_conf_fname), encoding=read_encoding)
            else:
                self._payload_conf_dict = conf.read_conf_from_file(
                    self.conf_path.joinpath(payload_conf_fname))

            # update page size
            if self._payload_conf_dict['payload'].get('page', None) is not None:
                if isinstance(self._payload_conf_dict['payload']['page'].get('size', None), int):
                    if self.page_size > self._payload_conf_dict['payload']['page']['size']:
                        self._payload_conf_dict['payload']['page']['size'] = self.page_size

            # change params in conf
            self._update_payload_params(day_range=day_range)

            if show_payload:
                log.info(f"payload: {json.dumps(self._payload_conf_dict['payload'])}")

            # add to dict of payloads
            self.payloads[payload_conf_fname] = self._payload_conf_dict['payload']
            return self._payload_conf_dict['payload']

    @request_task_msgs
    @send_request_with_dict
    def send_request(
            self, request_method: str, url: str,
            request_payloads: str = '', request_headers: str = '') -> dict or requests.Response:
        """send a request and return response

        send a request and return response.
        if response code not equal to 200, output the info of params for debug.

        Args:
            request_method: str
                the method to send request, must in ['POST', 'GET']
            url: str
                the url to send a request and get response
            request_payloads: dict, default ''
            request_headers: str, default ''
                the payload and header used to create request instead of those in RequestParams

        Returns:
            a dict of json type or requests.Response if response.json() failed
        """
        if request_method.upper() not in ['POST', 'GET']:
            raise ValueError('Invaild request_method[{}]. Please input POST or GET.'.format(request_method))

        headers = request_headers if request_headers else self.headers
        if request_payloads:
            response = requests.request(
                request_method,
                url=url,
                headers=headers,
                data=json.dumps(request_payloads)
            )
        else:
            response = requests.request(
                request_method,
                url=url,
                headers=headers
            )

        log.debug("response.text: %s", response.text)
        try:
            response_jsondict = response.json()
            log.debug("response_msg: %s", response_jsondict['msg'])
            if response_jsondict['code'] != 200:
                log.error("request failed.")
                log.warning(f"request_method: {request_method}")
                log.warning("response.text[:1000]: %s", response.text[:1000])
                log.warning(f"url: {url}", )
                log.warning("headers: {}".format(headers))
                log.warning("payload: {}".format(request_payloads))
            else:
                return response_jsondict
        except Exception:
            log.error('The response body does not contain valid json. Return requests.Response')
            log.error(f"request_method: {request_method}")
            log.error("response.text[:1000]: %s", response.text[:1000])
            log.error(f"url: {url}", )
            log.error("headers: {}".format(headers))
            log.error("payload: {}".format(request_payloads))
            return response

    def _update_payload_params(self, day_range: list = []) -> None:
        """update the params in readed payload"""
        if day_range:
            if self._payload_conf_dict['payload'].get('lastModifiedDateRange', None) is not None:
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
                self._payload_conf_dict['payload']['lastModifiedDateRange'] = [
                    s_date.strftime('%Y-%m-%d') + 'T16:00:00.000Z',
                    e_date.strftime('%Y-%m-%d') + 'T16:00:00.000Z',
                ]
                log.info("lastModifiedDateRange: %s", self._payload_conf_dict['payload']['lastModifiedDateRange'])
            else:
                log.warning('No lastModifiedDateRange in payload. Invaild day_range.')


if __name__ == '__main__':
    request_mgr = RequestManager()
    request_mgr.read_conf('settings.yaml')

    if False:
        # test headers and url_dict
        log.info(f"headers: {request_mgr.headers}")
        log.info(f"url of urlgetSql: {request_mgr.read_url('urlgetSql')}")

    if True:
        # test payload
        # payload = request_mgr.read_payload('excel\\excel_uncheck.yaml', show_payload=True)
        payload = request_mgr.read_payload('excel\\excel_check_tan_latest.yaml', show_payload=False, day_range=[-1, 0])
        # request_mgr.read_payload('poolchange\\poolchange_juno_error_inner.yaml', show_payload=False, no_page=True)
        log.info(f"payload: \n{json.dumps(payload)}")
        log.info(f"payloads: \n{request_mgr.payloads}")

    if True:
        # test send_request
        response = request_mgr.send_request(
            "POST",
            url=request_mgr.read_url('url'),
            request_payloads=payload
        )
        if response.get('code', None) is not None:
            log.info(f"code of response: {response['code']}")
            log.info(f"msg of response: {response['msg']}")
            if response.get('data', None) is not None:
                if response.get('total', None) is not None:
                    log.info(f"total of response: {response['data']['total']}")
        else:
            log.error('Failure requests')
