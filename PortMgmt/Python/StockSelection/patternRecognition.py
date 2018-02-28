'''
Created on Jan 10, 2018

@author: ywang
'''

# cd C:\Users\ywang\Desktop\Download\GitHub\MyProjects\PortMgmt\Python

import pandas as pd
from pandas import DataFrame, Series
import pandas_datareader.data as web

import numpy as np

import sqlalchemy
from urllib.parse import quote_plus

from datetime import datetime 

from StockSelection.sqlScript import sql_example

from scipy.interpolate import CubicSpline, UnivariateSpline
from scipy.optimize import root, fsolve

import matplotlib.pyplot as plt


def getLocalExtrema(f, x0):
    # Find all the local extrema for function f, given starting points x
    # f: function; scipy splin class
    # x: np.arange()

    df = f.derivative()
    x_extrema = fsolve(df, x0)
    
    x_extrema.sort()
    
    # Get rid of the duplicated values
    tag = np.diff(x_extrema) > 0.001
    tag = np.append([True], tag)
    
    x_uniq = x_extrema[tag]
    
    return x_uniq
    
    


def checkDoubleBottom(x, f):
    # Check if a pattern is double bottom
    # x: local extremas
    # f: function; scipy spline class
    pass
    
    
    
    


# Test sql
if __name__ == "__main__":
    
    params = quote_plus("DRIVER={SQL Server}; SERVER=ASTJ9K2Y52RESR\SYW_LOCAL_V2014; DATABASE=YFinData; Trusted_Connection=yes")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    
    df = pd.read_sql(sql_example, engine, index_col='Date')
    df = df[['Close', 'DailyTotalRet']]
    df = df.iloc[-500:,:]
    
    x = np.arange(500)
    y = df.Close.values
    
    spl = UnivariateSpline(x,y,k=3)
    xx = np.arange(0, 500, 0.1)
    
    plt.figure()
    
    plt.plot(x, y, 'o', ms=3, label='Data')
    plt.plot(xx, spl(xx), 'g', lw=1, label='s=N (Default)')
    
    k = 5
    spl.set_smoothing_factor(len(x)/k)
    plt.plot(xx, spl(xx), 'b', lw=1, label='s=N/'+str(k))
    
    loc_extrema = getLocalExtrema(spl, np.arange(0,500,20))
    plt.plot(loc_extrema, spl(loc_extrema), 'r+', label='loc_ex')
    
    plt.legend(loc='best')
    
    plt.show()
    
    
    
    
    
    
    
    
    
    
    