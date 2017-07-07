# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 09:37:04 2016

@author: ywang
"""

import pandas as pd
import pandas_datareader.data as web
import datetime 
import matplotlib.dates as mdates
import numpy as np

import xlwings as xw

import matplotlib.pyplot as plt
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc

import fix_yahoo_finance as yf
yf.pdr_override()

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
        # quote = quote.append(web.get_quote_yahoo(df.index[k*1000:(k+1)*1000]))
        quote = quote.append(web.get_quote_google(df.index[k*1000:(k+1)*1000]))
        k += 1
    # quote = quote.append(web.get_quote_yahoo(df.index[k*1000:]))
    quote = quote.append(web.get_quote_google(df.index[k*1000:]))
    quote.replace('N/A', np.nan, inplace=True)
    
    df['LastPrice'] = quote['last']
    df['CHG%'] = quote['change_pct']

    # Gest dist to target price
    df['DistToTarget'] = df['LastPrice'] / df['TargetPrice'] - 1
    df.loc[df.DistToTarget.isnull(), 'DistToTarget'] = 'N/A'
    
    if flag == 'Hist':
        # Get hist prices
        start = datetime.date.today() + datetime.timedelta(days=-52*7)
        
        # yahoo API is not working
        # data = web.DataReader(df.index, 'yahoo', start)
        # data = web.DataReader(df.index, 'google', start)
        data = web.get_data_yahoo(df.index.tolist(), start)
        
        # get previous close
        df['PrevClose'] = data.ix['Close', -1, :]
        df['CHG'] = df['LastPrice'] - df['PrevClose']
        
        # get 20D, 60D, 120D avg
        df['Avg20D'] = data.ix['Close', -20:, :].mean()
        df['Avg40D'] = data.ix['Close', -40:, :].mean()
        df['Avg120D'] = data.ix['Close', -120:, :].mean()
        
        df['DistToAvg20D'] = df['LastPrice'] / df['Avg20D'] - 1
        df['DistToAvg40D'] = df['LastPrice'] / df['Avg40D'] - 1
        df['DistToAvg120D'] = df['LastPrice'] / df['Avg120D'] - 1
        
        # get 52w max/min
        df['Max52W'] = data.ix['Close'].max()
        df['Min52W'] = data.ix['Close'].min()
        
        df['DistToMax52W'] = df['LastPrice'] / df['Max52W'] - 1
        df['DistToMin52W'] = df['LastPrice'] / df['Min52W'] - 1
    
    # Save Output
    tbl.value = df
    # return df, data

    
def updateBookLiveQuote():
    xb = xw.apps.active.books.active

    xb.sheets['OptionsHouse'].range('T1:T20').value = None
    for i, sht in enumerate(xb.sheets):
        if sht.name != 'Plot':
            xb.sheets['OptionsHouse'].range('T'+str(i+2)).value = 'Updating '+sht.name+'...'
            updateSheet(sht, 'LiveQuote')
    xb.sheets['OptionsHouse'].range('T'+str(i+2+1)).value = 'Complete!'
    

def updateBookAllHist():
    xb = xw.apps.active.books.active

    xb.sheets['OptionsHouse'].range('T1:T20').value = None
    for i, sht in enumerate(xb.sheets):
        if sht.name not in ['Plot', 'R3000']:
            xb.sheets['OptionsHouse'].range('T'+str(i+2)).value = 'Updating '+sht.name+'...'
            updateSheet(sht, 'Hist')
    xb.sheets['OptionsHouse'].range('T'+str(i+2+1)).value = 'Complete!'
    

def updateCurrentSheet():
    sht = xw.apps.active.books.active.sheets.active
    sht.range('T3').expand().clear()
    sht.range('T3').value= 'Updating ' + sht.name + '...'
    updateSheet(sht, 'Hist')
    sht.range('T4').value = 'Complete!'
    
    
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

    