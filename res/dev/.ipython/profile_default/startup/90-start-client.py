#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# flake8: noqa
'''
@File    :   90-start-client.py
@Author  :   Billy Zhou
@Time    :   2021/11/02
@Desc    :   None
'''


import sys
import yaml
from pathlib import Path
with open(Path(__file__).parent.joinpath('settings.yaml'), 'r', encoding='utf-8') as configfile:
    data = yaml.load(configfile, Loader=yaml.Loader)
if 'path_to_add' in data.keys():
    for path_to_add in data['path_to_add']:
        sys.path.append(str(Path(path_to_add)))  # add the path to your workspace root
else:
    sys.path.append(Path(sys.argv[0]).parent)

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

pd.options.display.max_columns = 500
pd.options.display.max_rows = 500

from src.manager.EngineManager import EngineManager
from src.utils.sql import sql_read
from src.utils.sql import sql_query
from src.utils.sql import sql_result_output

if __name__ == '__main__':
    manager = EngineManager()
    manager.read_conn_list()
