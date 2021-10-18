#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# flake8: noqa
'''
@File    :   90-start-client.py
@Author  :   Billy Zhou
@Time    :   2021/08/20
@Desc    :   None
'''


import sys
from pathlib import Path
sys.path.append("D:\pycharm\py_sql_client")  # change the path to your workspace root

from src.manager.EngineManager import EngineManager
from src.basic.sql_func import sql_read
from src.basic.sql_func import sql_query
from src.basic.sql_func import sql_result_output

if __name__ == '__main__':
    manager = EngineManager()
    manager.read_conn_list()
