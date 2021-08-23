#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   post_to_excel.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]
sys.path.append(str(cwdPath))

from src.manager.Logger import logger  # noqa: E402
log = logger.get_logger(__name__)

from src.basic.dataframe_func import records_to_df  # noqa: E402
from src.post.RequestParams import RequestParams  # noqa: E402


def post_for_records_list(request_params: RequestParams, payload_conf: str, max_page: int = 10):
    """post to get responses and combine multi records into a records_list

    Args:
        request_params: RequestParams
            a RequestParams instance
        payload_conf: str
            the name of payload_conf_fname to read from RequestParams
        max_page: int, default 10
            the maximum page num to get responses
    """
    response_dict = request_params.send_request(
        "POST", url=request_params.read_url('url'),
        payload_from_conf=payload_conf
    )
    if response_dict and isinstance(response_dict, dict):
        records_list = response_dict['data']['records']

        # loop if total bigger than size
        log.info("total: %s", response_dict['data']['total'])
        log.info("size: %s", response_dict['data']['size'])
        if int(response_dict['data']['total']) > int(response_dict['data']['size']):
            looptime = int(response_dict['data']['total']) // int(response_dict['data']['size']) + 1
            if looptime > max_page:
                looptime = max_page
            log.info("looptime: %s", looptime)
            for i in range(1, looptime):
                # update page param in payload
                request_params.update_payload_page(payload_conf, step=1)
                response_dict_looped = request_params.send_request(
                    "POST",
                    url=request_params.read_url('url'),
                    payload_from_conf=payload_conf
                )
                if response_dict_looped and isinstance(response_dict_looped, dict):
                    records_list.extend(response_dict_looped['data']['records'])

        return records_list


def post_to_excel(
        request_params: RequestParams, payload_conf: str,
        excel_fpath: str, excel_fname: str, col_list: list,
        day_range: list = [], max_page: int = 10, not_in_dict: dict = {},
        sample_num: bool = False):
    """post to get responses and output the result to a excel file

    Args:
        request_params: RequestParams
            a RequestParams instance
        payload_conf: str
            the name of payload_conf_fname to read from RequestParams
        excel_fpath: str
            the directory of output excel file
        excel_fname: str
            the filename of output excel file
        col_list: List[str]
            a list of colname to filter the converted dataframe
        day_range: list, default []
            a list of two datetime str to pass to request_params.read_payload

            For example, ["2021-08-22T00:00:00.000Z", "2021-08-23T00:00:00.000Z"]
        max_page: int, default 10
            the maximum page num to get responses
        not_in_dict: dict, default {}
            a dicf to exclude some values from the converted dataframe

            For example, {'id': ['1111']} will exclude the value '1111' in col named 'id'
        sample_num: int, default 0
            return a sample dataframe with sample_num rows as the final result
    """
    request_params.read_payload(payload_conf, show_payload=False, day_range=day_range)

    # get records_list
    records_list = post_for_records_list(request_params, payload_conf, max_page=max_page)

    # put records_list into excel
    if records_list:
        records_df = records_to_df(
            records_list,
            col_list_request=col_list,
            to_file=excel_fpath + excel_fname,
            not_in_dict=not_in_dict,
            sample_num=sample_num
        )
        log.debug("records_df: %s", records_df)
    else:
        log.warning("Blank records_list")


if __name__ == '__main__':
    request_params = RequestParams()
    request_params.read_conf('settings.yaml')

    import time
    post_to_excel(
        request_params,
        payload_conf='excel_uncheck.yaml',
        excel_fpath='D:\\zhouzp\\__working__\\_每日跟踪\\华泰分配\\',
        excel_fname='待稽核_{date}.xlsx'.format(
            date=time.strftime("%Y%m%d-%H%M%S", time.localtime())),
        col_list=['id', 'formYear', 'status', 'auditProcessName', 'fileName', 'subjectName', 'enableTypeName', 'suspensionName', 'taskPoolName'],
        max_page=100,
        sample_num=20
    )
