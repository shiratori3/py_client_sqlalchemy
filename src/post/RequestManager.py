#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   RequestParams.py
@Author  :   Billy Zhou
@Time    :   2021/09/18
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr  # noqa: E402
log = logmgr.get_logger(__name__)

import time
import datetime
import requests
from src.manager.main import conf  # noqa: E402


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
            the dict saving converted payload readed from conf_path.joinpath(payload_conf_fname)
            for example, {payload_conf_fname: _payload_str}
        payload_curpage_dict: dict
            the dict saving page param for each payload_conf_fname
            for example, {payload_conf_fname: cur_page}

    Methods:
    -------
        read_conf(self, conf_fname: str) -> None:
            read from conf_path.joinpath(conf_fname) and update headers
        read_url(self, url_type: str, **params) -> str:
            read url in self.url_dict and format with timestamp
        read_payload(
                self, payload_conf_fname: str,
                show_payload: bool = False, no_page: bool = False, day_range: list = []
            ) -> None:
            read payload from conf_path.joinpath(payload_conf_fname) and update params in payload
        update_payload_page(self, payload_conf_fname: str, step: int = 1):
            update page param in payload
        send_request(
                self, request_method: str, url: str,
                request_payloads: str = '', request_headers: str = ''
            ) -> dict or requests.Response:
            send a request and return response
    """
    def __init__(self, conf_path: Path = cwdPath.joinpath('conf/post')):
        self.conf_path = Path(conf_path)

        self.url_dict = {}
        self.payload_curpage_dict = {}
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
        if self.url_dict.get(url_type):
            return self.url_dict[url_type].format(timestamp=int(round(time.time() * 1000)), **params)
        else:
            log.error("Unvaild url_type. Return blank url.")
            return ''

    def read_payload(
            self, payload_conf_fname: str,
            show_payload: bool = False, no_page: bool = True, day_range: list = []) -> None:
        """read payload from conf_path.joinpath(payload_conf_fname) and update params in payload

        Args:
            payload_conf_fname: str
                the filename of payload conf to read
            show_payload: bool, default False
                show payload readed for debug
            no_page: bool, default False
                whether not to add page param in payload
            day_range: list, default []
                a list of two datetime str to update the 'lastModifiedDateRange' param in payload

                For example, ["2021-08-22T00:00:00.000Z", "2021-08-23T00:00:00.000Z"]
        """
        self._payload_conf_dict = conf.read_conf_from_file(self.conf_path.joinpath(payload_conf_fname))

        # init
        self.payload_curpage_dict[payload_conf_fname] = 1
        log.debug("payload_dict: %s", self._payload_conf_dict)

        # change params in conf
        self._update_payload_params(day_range=day_range)

        # convert dict to str
        self._payload_str = self._payload_dict2str(payload_conf_fname, no_page=no_page)
        if show_payload:
            log.info("payload: %s", self._payload_str)

        # add to dict of payload
        self.payloads[payload_conf_fname] = self._payload_str

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
            request_payloads: str, default ''
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
                data=request_payloads
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
            log.warning("response_msg: %s", response_jsondict['msg'])
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

    def update_payload_page(self, payload_conf_fname: str, step: int = 1):
        """update page param in payload"""
        self.payloads[payload_conf_fname] = self.payloads[payload_conf_fname].replace(
            '"current":' + str(self.payload_curpage_dict[payload_conf_fname]) + ',"',
            '"current":' + str(self.payload_curpage_dict[payload_conf_fname] + step) + ',"'
        )
        self.payload_curpage_dict[payload_conf_fname] += step

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

    def _payload_dict2str(self, payload_conf_fname: str, no_page: bool = False):
        """convert payload from dict to str for request"""
        log.debug("payload_conf_dict: {0}".format(self._payload_conf_dict))
        payload_param = str(self._payload_conf_dict["payload"]).replace('\'', '"').replace(' ', '').replace('None', 'null').replace('False', 'false').replace('True', 'true')
        if no_page:
            return payload_param
        else:
            # add page param
            return '{"page":{"current":' + str(self.payload_curpage_dict[payload_conf_fname]) + ',"size":' + str(self.page_size) + "}," + payload_param[1:-1] + "}"


if __name__ == '__main__':
    request_mgr = RequestManager()
    request_mgr.read_conf('settings.yaml')
    log.info("headers: %s", request_mgr.headers)

    url = request_mgr.read_url('urlgetSql')
    log.info("url: %s", url)

    request_mgr.read_payload('excel\\excel_uncheck.yaml', show_payload=True, no_page=False)
    request_mgr.read_payload('poolchange\\poolchange_juno_error_inner.yaml', show_payload=False, no_page=True)
    request_mgr.read_payload('excel\\excel_check_tan_latest.yaml', show_payload=False, no_page=False, day_range=[-1, 0])
    request_mgr.update_payload_page('excel\\excel_check_tan_latest.yaml', step=2)
    log.info("payloads: %s", request_mgr.payloads)
