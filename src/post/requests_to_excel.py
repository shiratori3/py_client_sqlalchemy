#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   requests_to_excel.py
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

from src.post.RequestManager import RequestManager  # noqa: E402
from src.basic.dataframe_func import records_to_df  # noqa: E402
from src.post.multi_requests import multi_requests_increment  # noqa: E402


def requests_to_excel(
        request_mgr: RequestManager, payload_conf: str,
        excel_fpath: str, col_list: list,
        day_range: list = [], max_page: int = 10,
        row_in_col_to_capture: dict = {}, row_in_col_to_discard: dict = {},
        sample_num: bool = False, timestamp_to_datetime: dict = {}):
    """post to get responses and output the result to a excel file

    Args:
        request_mgr: RequestParams
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
            a list of two datetime str to pass to request_mgr.read_payload

            For example, ["2021-08-22T00:00:00.000Z", "2021-08-23T00:00:00.000Z"]
        max_page: int, default 10
            the maximum page num to get responses
        row_in_col_to_capture: dict, default {}
        row_in_col_to_discard: dict, default {}
            a dict to filter rows in cols from the dataframe.
            diff cols will be combined by operator.or_
            a filter of string cols like '%row_string%' is accepted.

            For example,
            {'id': ['1111', '2222']} will include/exclude both of value '1111' and '2222' in col named 'id'
            {'id': ['%11%']} will include/exclude the string contains '11' in col named 'id'
        sample_num: int, default 0
            return a sample dataframe with sample_num rows as the final result
        timestamp_to_datetime: dict, default {}
            a dict to convert timestamp data in cols in the converted dataframe

            For example, {'lastModifiedDate': 'ms'} will convert the timestamps
            in col named 'lastModifiedDate' with pd.to_datetime(unit='ms')
    """
    # get records_list
    records_list = multi_requests_increment(request_mgr, payload_conf, max_limit=max_page, day_range=day_range)

    # put records_list into excel
    if records_list:
        records_df = records_to_df(
            records_list,
            col_list_request=col_list,
            to_file=excel_fpath,
            row_in_col_to_capture=row_in_col_to_capture,
            row_in_col_to_discard=row_in_col_to_discard,
            sample_num=sample_num,
            timestamp_to_datetime=timestamp_to_datetime
        )
        log.debug("records_df: %s", records_df)
    else:
        log.warning("Blank records_list")


if __name__ == '__main__':
    request_mgr = RequestManager()
    request_mgr.read_conf('settings.yaml')

    import time
    requests_to_excel(
        request_mgr,
        payload_conf='excel_check_tan_latest.yaml',
        excel_fpath='D:\\测试_{date}.xlsx'.format(
            date=time.strftime("%Y%m%d-%H%M%S", time.localtime())),
        col_list=['id', 'formYear', 'status', 'auditProcessName', 'fileName', 'subjectName', 'enableTypeName', 'suspensionName', 'taskPoolName'],
        max_page=100,
        sample_num=20
    )
