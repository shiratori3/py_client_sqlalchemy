#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   post_to_excel.py
@Author  :   Billy Zhou
@Time    :   2021/08/18
@Version :   1.6.0
@Desc    :   None
'''


import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2]))

from src.basic.dataframe_func import records_to_df  # noqa: E402
from src.post.RequestParams import RequestParams  # noqa: E402


def post_for_records_list(request_params: RequestParams, payload_conf: str, max_page=10):
    response_dict = request_params.send_request(
        "POST", url=request_params.read_url('url'),
        payload_from_conf=payload_conf
    )
    if response_dict and isinstance(response_dict, dict):
        records_list = response_dict['data']['records']

        # loop if total bigger than size
        logging.info("total: %s", response_dict['data']['total'])
        logging.info("size: %s", response_dict['data']['size'])
        if int(response_dict['data']['total']) > int(response_dict['data']['size']):
            looptime = int(response_dict['data']['total']) // int(response_dict['data']['size']) + 1
            if looptime > max_page:
                looptime = max_page
            logging.info("looptime: %s", looptime)
            for i in range(1, looptime):
                request_params.update_payload_page(payload_conf, step=1)
                response_dict_looped = request_params.send_request(
                    "POST",
                    url=request_params.read_url('url'),
                    payload_from_conf=payload_conf
                )
                if response_dict_looped and isinstance(response_dict_looped, dict):
                    records_list.extend(response_dict_looped['data']['records'])

        logging.debug("records_list: %s", records_list)

        return records_list


def post_to_excel(
        request_params: RequestParams, payload_conf: str, excel_fpath, excel_fname, col_list,
        max_page=10, not_in_dict={}, day_range=[], sample_num=False):
    request_params.read_payload(payload_conf, show_payload=False, day_range=day_range)

    # get records_list
    records_list = post_for_records_list(request_params, payload_conf, max_page=max_page)

    # put records_list into excel
    if records_list:
        records_df = records_to_df(
            records_list,
            col_list,
            to_file=excel_fpath + excel_fname,
            not_in_dict=not_in_dict,
            sample_num=sample_num
        )
        logging.debug("records_df: %s", records_df)
    else:
        logging.warning("Blank records_list")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

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

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
