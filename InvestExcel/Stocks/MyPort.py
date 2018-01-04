# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 09:37:04 2016

@author: ywang
"""

import pandas as pd
import pandas_datareader.data as web
from pandas_datareader._utils import RemoteDataError

import datetime 
import matplotlib.dates as mdates
import numpy as np

import xlwings as xw

import matplotlib.pyplot as plt
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc


@xw.func
def myplot(ticker, weeks):
    # Get hist prices
    start = datetime.date.today() + datetime.timedelta(days=-weeks*7)

    # data = web.DataReader(ticker, 'yahoo', start)
    data = web.get_data_yahoo(ticker, start)
    
    # try 1
    # ax = data['Close'].plot(title=ticker)
    # fig = ax.get_figure()
    
    # try 2
    fig = plt.figure()
    plt.plot(data.index, data.Close)

    ax = plt.axes()
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
    ax.set_title(ticker)
    
    fig.autofmt_xdate()

    sht = xw.Book.caller().sheets.active
    sht.pictures.add(fig, name='52W', update=True, left=sht.range('B5').left, top=sht.range('B5').top)

    return str(int(weeks))+'W Price Plot'
    
@xw.func
def myplot_candlestick(ticker, weeks):
    start = datetime.date.today() + datetime.timedelta(days=-weeks*7)
    
    quotes = quotes_historical_yahoo_ohlc(ticker, start, datetime.date.today())
    
    fig = plt.figure()
    ax = plt.axes()
    
    candlestick_ohlc(ax, quotes, width=0.6)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
    fig.autofmt_xdate()
    
    ax.set_title(ticker)
    
    sht = xw.Book.caller().sheets.active
    sht.pictures.add(fig, name='52W', update=True, left=sht.range('B5').left, top=sht.range('B5').top)

    return str(int(weeks))+'W Candlestick Plot'

def updateSheet(sht, flag='LiveQuote'):
    # update the sh
    # sht = xb.sheets[shtName]
    tbl = sht.range('A1').expand().options(pd.DataFrame, expand='table')
    
    df = tbl.value
    
    # pull live data, 1000 tickers each time
    quote = pd.DataFrame()
    k = 0
    while df.index.shape[0] > (k+1)*1000:
        quote = quote.append(web.get_quote_yahoo(df.index[k*1000:(k+1)*1000]))
        # quote = quote.append(web.get_quote_google(df.index[k*1000:(k+1)*1000]))
        k += 1
    quote = quote.append(web.get_quote_yahoo(df.index[k*1000:]))
    # quote = quote.append(web.get_quote_google(df.index[k*1000:]))
    quote.replace('N/A', np.nan, inplace=True)
    
    df['LastPrice'] = quote['last']
    df['CHG%'] = quote['change_pct']

    # Gest dist to target price
    # df['DistToTarget'] = df['LastPrice'] / df['TargetPrice'] - 1
    # df.loc[df.DistToTarget.isnull(), 'DistToTarget'] = 'N/A'
    
    if flag == 'Hist':
        # Get hist prices
        start = datetime.date.today() + datetime.timedelta(days=-52*7)
        
        # yahoo API is not working
        # data = web.DataReader(df.index, 'yahoo', start)
        # data = web.DataReader(df.index, 'google', start)
        dict_data = {}
        for ticker in df.index:
            sht.range('X3').value = ['Pull Data: ', ticker]
            try:
                dict_data[ticker] = web.DataReader(ticker, 'yahoo', start)
            except RemoteDataError:
                sht.range('X3').value = ['Pull Data: ', ticker]
                dict_data[ticker] = pd.DataFrame()
                
            if dict_data[ticker].shape[0] > 0:
                # get previous close
                idx = dict_data[ticker].index
                df.loc[ticker, 'PrevClose'] = dict_data[ticker].loc[idx[-1], 'Close']
                df.loc[ticker, 'CHG'] = df.loc[ticker, 'LastPrice'] - df.loc[ticker, 'PrevClose']
                
                # get 20D, 60D, 120D avg
                df.loc[ticker, 'Avg20D'] = dict_data[ticker].loc[idx[-20:], 'Close'].mean()
                df.loc[ticker, 'Avg40D'] = dict_data[ticker].loc[idx[-40:], 'Close'].mean()
                df.loc[ticker, 'Avg120D'] = dict_data[ticker].loc[idx[-120:], 'Close'].mean()
                
                df.loc[ticker, 'DistToAvg20D'] = df.loc[ticker, 'LastPrice'] / df.loc[ticker, 'Avg20D'] - 1
                df.loc[ticker, 'DistToAvg40D'] = df.loc[ticker, 'LastPrice'] / df.loc[ticker, 'Avg40D'] - 1
                df.loc[ticker, 'DistToAvg120D'] = df.loc[ticker, 'LastPrice'] / df.loc[ticker, 'Avg120D'] - 1
                
                # get 52w max/min
                df.loc[ticker, 'Max52W'] = dict_data[ticker]['Close'].max()
                df.loc[ticker, 'Min52W'] = dict_data[ticker]['Close'].min()
                
                df.loc[ticker, 'DistToMax52W'] = df.loc[ticker, 'LastPrice'] / df.loc[ticker, 'Max52W'] - 1
                df.loc[ticker, 'DistToMin52W'] = df.loc[ticker, 'LastPrice'] / df.loc[ticker, 'Min52W'] - 1
    
    # Save Output
    tbl.value = df
    # return df, data

    
def updateBookLiveQuote():
    xb = xw.apps.active.books.active

    xb.sheets['OptionsHouse'].range('X1:X20').value = None
    for i, sht in enumerate(xb.sheets):
        if sht.name != 'Plot':
            xb.sheets['OptionsHouse'].range('X'+str(i+2)).value = 'Updating '+sht.name+'...'
            updateSheet(sht, 'LiveQuote')
    xb.sheets['OptionsHouse'].range('X'+str(i+2+1)).value = 'Complete!'
    

def updateBookAllHist():
    xb = xw.apps.active.books.active

    xb.sheets['OptionsHouse'].range('X3:X20').value = None
    for i, sht in enumerate(xb.sheets):
        if sht.name not in ['Plot', 'R3000']:
            xb.sheets['OptionsHouse'].range('X'+str(i+2)).value = 'Updating '+sht.name+'...'
            updateSheet(sht, 'Hist')
    xb.sheets['OptionsHouse'].range('X'+str(i+2+1)).value = 'Complete!'
    

def updateCurrentSheet():
    sht = xw.apps.active.books.active.sheets.active
    sht.range('X3').expand().clear()
    sht.range('X3').value= 'Updating ' + sht.name + '...'
    updateSheet(sht, 'Hist')
    sht.range('X4').value = 'Complete!'
    
    
#==============================================================================
# Main Script
#==============================================================================
    
if __name__ == "__main__":
    
    xb = xw.books.open('MyPort.xlsm')
    
    xb.sheets[1].range('T1:T20').value = None
    for sht in xb.sheets:
        if sht.name != 'Plot':
            xb.sheets[1].range('T2').value = 'Updating '+sht.name
            print('Updating '+sht.name)
            updateSheet(sht, 'Hist')

    