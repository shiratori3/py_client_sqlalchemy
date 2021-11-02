#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   excel_func.py
@Author  :   Billy Zhou
@Time    :   2021/10/26
@Desc    :   None
'''


import sys
from pathlib import Path
cwdPath = Path(__file__).parents[2]  # the num depend on your filepath
sys.path.append(str(cwdPath))

from src.manager.LogManager import logmgr
log = logmgr.get_logger(__name__)

import xlwings as xw
from src.excel.sheet_func import sum_sheets


def sum_excelfile(sum_path: Path, output_filename: str, drop_existed: bool = True):
    '''summary the excel files under sum_path into output_filename'''
    # check the vaild of output_filename
    if Path(output_filename).suffix not in ('.xlsx', '.xls'):
        raise ValueError(f'unvaild filename {output_filename}')

    # check output_file exists or not
    sum_path = Path(sum_path)
    output_filepath = sum_path.joinpath(output_filename)
    if output_filepath.exists():
        if drop_existed:
            try:
                output_filepath.unlink()
            except PermissionError as e:
                log.error('An error occurred. {}'.format(e.args[-1]))
                log.warning(f'{output_filepath} is using. Force to close')
                xw.books.open(output_filepath).close()
                output_filepath.unlink()
                log.warning(f'{output_filepath} is deleted.')
        else:
            raise FileExistsError(f'{output_filename} already exists under {sum_path}')

    if not xw.apps.count:
        wb = xw.Book()
    else:
        app = xw.apps.active
        wb = app.books.add()
    wb.save(str(output_filepath))
    sum_sheets(0, suffix=".xls", only_copy_first_sheet=True, target_cur_sht=True)
    sum_sheets(0, suffix=".xlsx", only_copy_first_sheet=True, target_cur_sht=True)
    wb.save(str(output_filepath))
    wb.close()


if __name__ == '__main__':
    import time
    excelfile_savepath = 'D:\\zhouzp\\__working__\\sqlresult'
    sum_filename = '{date}-错别字汇总-周梓鹏.xlsx'.format(date=time.strftime('%Y-%m-%d', time.localtime()))
    sum_excelfile(excelfile_savepath, sum_filename)
