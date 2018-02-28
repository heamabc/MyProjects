"""
Created on Mon Feb 28 2017

A Python data download tool just like Bloomberg Excel Addon

@author: ywang
"""


import pandas as pd
import pandas_datareader.data as web
import datetime 
import matplotlib.dates as mdates
import numpy as np

import xlwings as xw

@xw.func
@xw.ret(expand='table') # using dynamic array
def pullReturn(ticker, start_dt, end_dt, freq):
    ''' 
    Get historical total returns from Yahoo Finance.
    '''

    data = web.DataReader(ticker, 'yahoo', start_dt, end_dt)
    
    if freq in ['D', 'Day', 'Daily']:
        Ret = data['Adj Close'].pct_change()
        Ret.name = 'ReturnDaily'
    elif freq in ['M', 'Month', 'Monthly']:
        Ret = data['Adj Close'].resample('M').last().pct_change()
        Ret.name = 'ReturnMonthly'
    
    return Ret

@xw.func
def double_sum(x, y):
    """Returns twice the sum of the two arguments"""
    return 2*(x+y)

