#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# flake8: noqa
'''
@File    :   start.py
@Author  :   Billy Zhou
@Time    :   2021/03/12
@Version :   1.1.0
@Desc    :   None
'''


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

pd.options.display.max_columns = 500
pd.options.display.max_rows = 500

# 让notebook展示的区域更加宽
from IPython.core.display import display, HTML
WIDTH_85 = HTML("<style>.container { width:85% !important; }</style>")
WIDTH_100 = HTML("<style>.container { width:100% !important; }</style>")

from IPython import get_ipython
ipython = get_ipython()

# 每次底层包有变动，会自动加载
if 'ipython' in globals() and ipython:
    print('\nWelcome to IPython!')
    ipython.magic('load_ext autoreload')
    ipython.magic('autoreload 2')
    ipython.magic('matplotlib inline')

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'


if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('start DEBUG')
    logging.debug('==========================================================')

    import os
    from pathlib import Path

    usr_path = os.path.expanduser('~')
    filepath = Path(os.path.expanduser('~')).joinpath('.ipython\profile_default\startup')
    print('path_to_put: {0}'.format(filepath))

    print('dir: {0}'.format(dir()))
    print('globals: {0}'.format(globals()))

    logging.debug('==========================================================')
    logging.debug('end DEBUG')
